CREATE PROCEDURE dbo.UpsertDimDate
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if Dim_Date table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Date')
    BEGIN
        CREATE TABLE Dim_Date (
            sale_date DATE,
            day_name VARCHAR(20),
            day_of_month INT,
            day_of_week INT,
            month INT,
            year INT,
            week_of_year INT
        );
    END

    -- Update existing records
    UPDATE target_data
    SET
        target_data.day_name = DATENAME(WEEKDAY, source_data.sale_date),
        target_data.day_of_month = DAY(source_data.sale_date),
        target_data.day_of_week = DATEPART(WEEKDAY, source_data.sale_date),
        target_data.month = MONTH(source_data.sale_date),
        target_data.year = YEAR(source_data.sale_date),
        target_data.week_of_year = DATEPART(WEEK, source_data.sale_date)
    FROM Dim_Date AS target_data
    INNER JOIN Silver.Supply_Chain.Cleansed_sales AS source_data
        ON target_data.sale_date = CAST(source_data.sale_date AS DATE);

    -- Insert new records
    INSERT INTO Dim_Date (sale_date, day_name, day_of_month, day_of_week, month, year, week_of_year)
    SELECT DISTINCT
        CAST(sale_date AS DATE) AS sale_date,
        DATENAME(WEEKDAY, sale_date) AS day_name,
        DAY(sale_date) AS day_of_month,
        DATEPART(WEEKDAY, sale_date) AS day_of_week,
        MONTH(sale_date) AS month,
        YEAR(sale_date) AS year,
        DATEPART(WEEK, sale_date) AS week_of_year
    FROM Silver.Supply_Chain.Cleansed_sales AS source_data
    WHERE NOT EXISTS (
        SELECT 1
        FROM Dim_Date AS target_data
        WHERE target_data.sale_date = CAST(source_data.sale_date AS DATE)
    );
END