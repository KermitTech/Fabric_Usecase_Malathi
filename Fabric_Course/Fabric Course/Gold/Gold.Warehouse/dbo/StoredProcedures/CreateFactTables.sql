CREATE PROCEDURE dbo.CreateFactTables
AS
BEGIN
    SET NOCOUNT ON;

    -- Step 1: Ensure Fact_Sales table exists
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Fact_Sales')
    BEGIN
        CREATE TABLE Fact_Sales (
            transaction_id INT,
            customer_id INT,
            date_key DATE,
            month_key INT,
            year_key INT,
            product_key VARCHAR(100),
            store_key VARCHAR(100),
            quantity INT,
            unit_price DECIMAL(18, 2),
            discount DECIMAL(18, 2),
            total_amount DECIMAL(18, 2)
        );
    END;

    -- Step 2: Ensure Fact_Demand_Forecasting table exists
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Fact_Demand_Forecasting')
    BEGIN
        CREATE TABLE Fact_Demand_Forecasting (
            date_key DATE,
            month_key INT,
            year_key INT,
            product_key VARCHAR(100),
            store_key VARCHAR(100),
            total_quantity_sold INT,
            total_quantity_shipped INT,
            quantity_in_stock INT,
            stock_level INT,
            predicted_sales DECIMAL(10,2)
        );
    END;

    -- Step 3: Update existing records in Fact_Sales
    UPDATE fs
    SET
        fs.month_key = d.month,
        fs.year_key = d.year,
        fs.quantity = s.quantity,
        fs.customer_id = s.customer_id,
        fs.unit_price = s.unit_price,
        fs.discount = s.discount,
        fs.total_amount = s.sales_amount,
        fs.date_key = s.sale_date,
        fs.store_key = s.store_id,
        fs.product_key = s.product_id
    FROM Fact_Sales fs
    INNER JOIN Silver.Supply_Chain.Cleansed_sales s
        ON fs.transaction_id = s.transaction_id
    INNER JOIN Dim_Date d
        ON CAST(s.sale_date AS DATE) = d.date_key;

    -- Step 4: Insert new records into Fact_Sales
    INSERT INTO Fact_Sales (transaction_id, customer_id, date_key, month_key, year_key, product_key, store_key, quantity, unit_price, discount, total_amount)
    SELECT
        s.transaction_id,
        s.customer_id,
        CAST(s.sale_date AS DATE) AS date_key,
        d.month AS month_key,
        d.year AS year_key,
        s.product_id AS product_key,
        s.store_id AS store_key,
        s.quantity,
        s.unit_price,
        s.discount,
        s.sales_amount AS total_amount
    FROM Silver.Supply_Chain.Cleansed_sales s
    JOIN Dim_Date d ON CAST(s.sale_date AS DATE) = d.date_key
    WHERE NOT EXISTS (
        SELECT 1
        FROM Fact_Sales fs
        WHERE fs.transaction_id = s.transaction_id
          AND fs.date_key = CAST(s.sale_date AS DATE)
          AND fs.product_key = s.product_id
          AND fs.store_key = s.store_id
    );


-- Step 2: Update existing records
   UPDATE fd
   SET
        fd.total_quantity_sold = df.TotalQuantitySold,
        fd.total_quantity_shipped = df.TotalQuantityShipped,
        fd.quantity_in_stock = df.quantity_in_stock,
        fd.stock_level = df.StockLevel,
        fd.predicted_sales = ROUND(COALESCE(p.prediction, 0), 2)
    FROM Fact_Demand_Forecasting fd
    INNER JOIN Silver.Supply_Chain.Demand_Forecasting_Sales_Analysis df
        ON fd.date_key = CAST(df.Date AS DATE)
        AND fd.product_key = df.product_id
        AND fd.store_key = df.store_id
    LEFT JOIN Silver.Supply_Chain.Demand_Predictions p
        ON df.product_id = p.product_id
        AND df.store_id = p.store_id;

-- Step 3: Insert new records
    INSERT INTO Fact_Demand_Forecasting (date_key, month_key, year_key, product_key, store_key, total_quantity_sold, total_quantity_shipped, quantity_in_stock, stock_level, predicted_sales)
    SELECT
       CAST(df.Date AS DATE) AS date_key,
       df.Month AS month_key,
       df.Year AS year_key,
       df.product_id AS product_key,
       df.store_id AS store_key,
       df.TotalQuantitySold,
       df.TotalQuantityShipped,
       df.quantity_in_stock,
       df.StockLevel,
       ROUND(COALESCE(p.prediction, 0), 2) AS predicted_sales
    FROM Silver.Supply_Chain.Demand_Forecasting_Sales_Analysis df
    LEFT JOIN Silver.Supply_Chain.Demand_Predictions p
        ON df.product_id = p.product_id
        AND df.store_id = p.store_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM Fact_Demand_Forecasting fd
        WHERE fd.date_key = CAST(df.Date AS DATE)
          AND fd.product_key = df.product_id
          AND fd.store_key = df.store_id
    );

END;