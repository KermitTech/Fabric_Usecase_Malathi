CREATE   PROCEDURE sp_ReconciliationReport
    @BatchID INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Step 1: Declare variables for expected values
    DECLARE @MaxValue_Expected DATETIME;
    DECLARE @BatchID_Expected INT;

    -- Step 2: Retrieve expected values from the Control_Table
    SELECT 
        @MaxValue_Expected = MaxValue,
        @BatchID_Expected = BatchValue
    FROM [Campaign_Bronze_Layer].[salesforce].[Control_Table]
    WHERE TableName = 'Organisation'
      AND BatchValue = @BatchID;

    -- Step 3: Create a temporary table for reconciliation report
    CREATE TABLE #ReconciliationReport (
        TableName VARCHAR(100),
        MaxValue_Expected DATETIME,
        MaxValue_Actual DATETIME,
        BatchID_Expected INT,
        BatchID_Actual INT,
        Discrepancy VARCHAR(500)
    );

    -- Step 4: Insert actual values and compare them with expected values

    -- Organisation
    INSERT INTO #ReconciliationReport
    SELECT 
        'Organisation' AS TableName,
        @MaxValue_Expected AS MaxValue_Expected,
        MAX(CreatedDate) AS MaxValue_Actual,
        @BatchID_Expected AS BatchID_Expected,
        MAX(Batch_id) AS BatchID_Actual,
        CASE
            WHEN @MaxValue_Expected <> MAX(CreatedDate) THEN 'Mismatch in MaxValue'
            WHEN @BatchID_Expected <> MAX(Batch_id) THEN 'Mismatch in BatchID'
            ELSE 'No Discrepancy'
        END AS Discrepancy
    FROM [Campaign_Bronze_Layer].[salesforce].[Organisation]
    WHERE Batch_id = @BatchID;

    -- Tmp_Organisation
    INSERT INTO #ReconciliationReport
    SELECT 
        'Tmp_Organisation' AS TableName,
        @MaxValue_Expected AS MaxValue_Expected,
        MAX(CreatedDate) AS MaxValue_Actual,
        @BatchID_Expected AS BatchID_Expected,
        MAX(Batch_id) AS BatchID_Actual,
        CASE
            WHEN @MaxValue_Expected <> MAX(CreatedDate) THEN 'Mismatch in MaxValue'
            WHEN @BatchID_Expected <> MAX(Batch_id) THEN 'Mismatch in BatchID'
            ELSE 'No Discrepancy'
        END AS Discrepancy
    FROM [Campaign_Bronze_Layer].[salesforce].[Tmp_Organisation]
    WHERE Batch_id = @BatchID;

    -- Staging_Organisation
    INSERT INTO #ReconciliationReport
    SELECT 
        'Staging_Organisation' AS TableName,
        @MaxValue_Expected AS MaxValue_Expected,
        MAX(CreatedDate) AS MaxValue_Actual,
        @BatchID_Expected AS BatchID_Expected,
        MAX(Batch_id) AS BatchID_Actual,
        CASE
            WHEN @MaxValue_Expected <> MAX(CreatedDate) THEN 'Mismatch in MaxValue'
            WHEN @BatchID_Expected <> MAX(Batch_id) THEN 'Mismatch in BatchID'
            ELSE 'No Discrepancy'
        END AS Discrepancy
    FROM [Silver_Layer].[Salesforce_CRM].[staging_organisation]
    WHERE Batch_id = @BatchID;

    -- Step 5: Output the reconciliation report
    SELECT * FROM #ReconciliationReport;

    -- Step 6: Clean up temporary table
    DROP TABLE #ReconciliationReport;
END;