CREATE PROCEDURE GetCustReconciliation
    @EntityName VARCHAR(50)   -- Input parameter for entity_name
AS
BEGIN
    /*********************** Sales ****************************/

    /* Reconciliation count query for Source and target data */
    WITH RecentErrors AS (
        SELECT *
        FROM [Silver_Layer].[gold_layer_campaign].[Error_log_details]
        WHERE entity_name = @EntityName
          AND created_date = (
              SELECT MAX(created_date)
              FROM [Silver_Layer].[gold_layer_campaign].[Error_log_details]
              WHERE entity_name = @EntityName
          )
    ),
    SourceTargetCounts AS (
        SELECT 
            'Cleansed_count' AS Data_count, 
            COUNT(1) AS record_count 
        FROM [Silver_Layer].[Campaign].[cleansed_campaign]
        
        UNION ALL
        
        SELECT 
            'Errored_count' AS Data_count, 
            COUNT(1) AS record_count 
        FROM RecentErrors
    )
    SELECT 
        'Customer Interaction' as Entity,
        ISNULL([Cleansed_count], 0) + ISNULL([Errored_count], 0) AS Total_Source_Count,
        ISNULL([Cleansed_count], 0) AS Cleansed_count, 
        ISNULL([Errored_count], 0) AS Errored_count
    FROM 
        SourceTargetCounts
    PIVOT (
        MAX(record_count) FOR Data_count IN ([Cleansed_count], [Errored_count])
    ) AS PivotTable;

    /* Reconciliation query for error data */
    SELECT *
    FROM [Silver_Layer].[gold_layer_campaign].[Error_log_details]
    WHERE entity_name = @EntityName
      AND created_date = (
          SELECT MAX(created_date)
          FROM [Silver_Layer].[gold_layer_campaign].[Error_log_details]
          WHERE entity_name = @EntityName
      );
END;