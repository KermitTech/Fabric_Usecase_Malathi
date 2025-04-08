CREATE PROCEDURE dbo.UpsertFactSales
AS
BEGIN
    SET NOCOUNT ON;

    -- Step 1: Ensure the Fact_Sales table exists
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Fact_Sales')
    BEGIN
        CREATE TABLE Fact_Sales (
            transaction_id INT,
            date_key DATE,
            month_key INT,
            year_key INT,
            product_key varchar(100),
            store_key varchar(100),
            quantity INT,
            unit_price DECIMAL(18, 2),
            discount DECIMAL(18, 2),
            total_amount DECIMAL(18, 2)
        );
    END;

    -- Step 2: Update existing records
    UPDATE fs
    SET
        fs.month_key = d.month,
        fs.year_key = d.year,
        fs.quantity = s.quantity,
        fs.unit_price = s.unit_price,
        fs.discount = s.discount,
        fs.total_amount = s.sales_amount
    FROM Fact_Sales fs
    INNER JOIN Silver.Supply_Chain.Cleansed_sales s
        ON fs.transaction_id = s.transaction_id
    INNER JOIN Dim_Date d
        ON CAST(s.sale_date AS DATE) = d.sale_date
    INNER JOIN Dim_Product p
        ON s.product_id = p.product_id
    INNER JOIN Dim_Store st
        ON s.store_id = st.store_id;

    -- Step 3: Insert new records
    INSERT INTO Fact_Sales (transaction_id, date_key, month_key, year_key, product_key, store_key, quantity, unit_price, discount, total_amount)
    SELECT
        s.transaction_id,
        CAST(s.sale_date AS DATE) AS date_key,
        d.month AS month_key,
        d.year AS year_key,
        p.product_id AS product_key,
        st.store_id AS store_key,
        s.quantity,
        s.unit_price,
        s.discount,
        s.sales_amount AS total_amount
    FROM Silver.Supply_Chain.Cleansed_sales s
    JOIN Dim_Date d ON CAST(s.sale_date AS DATE) = d.sale_date
    JOIN Dim_Product p ON s.product_id = p.product_id
    JOIN Dim_Store st ON s.store_id = st.store_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM Fact_Sales fs
        WHERE fs.transaction_id = s.transaction_id
          AND fs.date_key = CAST(s.sale_date AS DATE)
          AND fs.product_key = p.product_id
          AND fs.store_key = st.store_id
    );
END;