-- Step 1: Create the stored procedure with a parameter for batch_id
CREATE PROCEDURE Reconcile_Data (@BatchID INT)
AS
BEGIN
    -- Step 2: Check if the target reconciliation table exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Reconciliation_Report')
    BEGIN
        -- If the table doesn't exist, create it (we don't specify default values here)
        CREATE TABLE Reconciliation_Report (
            TableName VARCHAR(100),
            MaxValue_Expected DATETIME,
            MaxValue_Actual DATETIME,
            BatchID_Expected INT,
            BatchID_Actual INT,
            Discrepancy VARCHAR(500),
            Insert_Count INT,
            Update_Count INT,
            RunTimestamp DATETIME -- This will be populated during insert
        );
    END

    -- Step 3: Retrieve the expected values from the Control_Table for all entities
    ;WITH ExpectedValues AS (
        SELECT 
            TableName,
            MaxValue AS MaxValue_Expected,
            BatchValue AS BatchID_Expected
        FROM [Campaign_Bronze_Layer].[salesforce].[Control_Table]
        WHERE TableName IN ('Organisation', 'Opportunities', 'Contact', 'Tmp_Organisation', 'Tmp_Opportunities', 'Tmp_Contact', 'Staging_Organisation', 'Staging_Opportunities', 'Staging_Contact')
    )
    
    -- Step 4: Insert reconciliation data into the reconciliation table
    INSERT INTO Reconciliation_Report (TableName, MaxValue_Expected, MaxValue_Actual, BatchID_Expected, BatchID_Actual, Discrepancy, Insert_Count, Update_Count, RunTimestamp)
    SELECT 
        t.TableName,
        ev.MaxValue_Expected,
        MAX(t.CreatedDate) AS MaxValue_Actual,
        ev.BatchID_Expected,
        MAX(t.Batch_id) AS BatchID_Actual,
        CASE
            WHEN ev.MaxValue_Expected <> MAX(t.CreatedDate) THEN 'Mismatch in MaxValue'
            WHEN ev.BatchID_Expected <> MAX(t.Batch_id) THEN 'Mismatch in BatchID'
            ELSE 'No Discrepancy'
        END AS Discrepancy,
        -- Count the number of inserts and updates based on Load_Type
        -- Use CASE to count Insert and Update operations INSIDE the aggregation query
        SUM(CASE WHEN t.Load_Type = 'Insert' THEN 1 ELSE 0 END) AS Insert_Count,
        SUM(CASE WHEN t.Load_Type = 'Update' THEN 1 ELSE 0 END) AS Update_Count,
        GETDATE() AS RunTimestamp -- Insert the current timestamp during each run
    FROM (
        -- Combine the data from all tables with aggregation for Insert and Update counts
        SELECT 'Organisation' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Organisation' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Staging_Organisation' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Silver_Layer].[Salesforce_CRM].[Staging_Organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Opportunities' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Opportunities]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Opportunities' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Opportunities]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Staging_Opportunities' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Silver_Layer].[Salesforce_CRM].[Staging_Opportunities]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Contact' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Contact]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Contact' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Contact]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Staging_Contact' AS TableName, CreatedDate, Batch_id, Load_Type
        FROM [Silver_Layer].[Salesforce_CRM].[Staging_Contact]
        WHERE Batch_id = @BatchID
    ) t
    LEFT JOIN ExpectedValues ev
        ON t.TableName = ev.TableName
    GROUP BY t.TableName, ev.MaxValue_Expected, ev.BatchID_Expected;

END;