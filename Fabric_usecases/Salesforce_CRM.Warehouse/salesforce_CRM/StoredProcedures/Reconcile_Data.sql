-- Step 1: Create the stored procedure with a parameter for batch_id
CREATE PROCEDURE [salesforce_CRM].[Reconcile_Data] (@BatchID INT)
AS
BEGIN

    --Truncate the table
    --TRUNCATE TABLE [salesforce_CRM].[Reconciliation_Report];

    -- Step 2: Check if the target reconciliation table exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Reconciliation_Report')
    BEGIN
        -- If the table doesn't exist, create it (we don't specify default values here)
        CREATE TABLE [salesforce_CRM].[Reconciliation_Report] (
            TableName VARCHAR(100),
            MaxValue_Expected DATETIME2(3),
            MaxValue_Actual DATETIME2(3),
            BatchID_Expected INT,
            BatchID_Actual INT,
            MaxValue_Discrepancy VARCHAR(500),
            BatchID_Discrepancy VARCHAR(500),
            RunTimestamp DATETIME2(3) -- This will be populated during insert
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
    INSERT INTO [salesforce_CRM].[Reconciliation_Report] (TableName, MaxValue_Expected, MaxValue_Actual, BatchID_Expected, BatchID_Actual, MaxValue_Discrepancy, BatchID_Discrepancy, RunTimestamp)
    SELECT 
        t.TableName,
        coalesce(ev.MaxValue_Expected,CAST('1991-01-01' AS DATETIME)) as MaxValue_Expected,
        COALESCE(CAST(MAX([CreatedDate]) AS DATETIME), CAST('1991-01-01' AS DATETIME)) AS MaxValue_Actual,
        coalesce(ev.BatchID_Expected, 0) as BatchID_Expected,
        coalesce(MAX(t.Batch_id), 0) AS BatchID_Actual,
        CASE
            WHEN coalesce(ev.MaxValue_Expected,CAST('1991-01-01' AS DATETIME)) <> COALESCE(CAST(MAX([CreatedDate]) AS DATETIME), CAST('1991-01-01' AS DATETIME)) THEN 'Mismatch in MaxValue'
            ELSE 'No Discrepancy'
        END AS MaxValue_Discrepancy,
        CASE
            WHEN coalesce(ev.BatchID_Expected, 0) <> coalesce(MAX(t.Batch_id), 0) THEN 'Mismatch in BatchID'
            ELSE 'No Discrepancy'
        END AS BatchID_Discrepancy,
        SYSDATETIME() AS RunTimestamp -- Insert the current timestamp during each run
    FROM (
        -- Combine the data from all tables with aggregation for Insert and Update counts
        SELECT 'Organisation' AS TableName, CreatedDate, Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Organisation' AS TableName, CreatedDate, Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Staging_Organisation' AS TableName, CreatedDate, Batch_id
        FROM [Silver_Layer].[Salesforce_CRM].[staging_organisation]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Opportunities' AS TableName, CreatedDate, Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Opportunities]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Opportunities' AS TableName, CreatedDate, null as Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Opportunities]
        --WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Contact' AS TableName, CreatedDate, Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Contact]
        WHERE Batch_id = @BatchID
        
        UNION ALL
        
        SELECT 'Tmp_Contact' AS TableName, CreatedDate, null as Batch_id
        FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Contact]
       -- WHERE Batch_id = @BatchID
        
    ) t
    LEFT JOIN ExpectedValues ev
        ON t.TableName = ev.TableName
    GROUP BY t.TableName, coalesce(ev.MaxValue_Expected,CAST('1991-01-01' AS DATETIME)),
        coalesce(ev.BatchID_Expected, 0)

END;