CREATE PROCEDURE dbo.CreateDimTables
AS
BEGIN
    SET NOCOUNT ON;

    -- ✅ Check if Dim_Product table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Product')
    BEGIN
        CREATE TABLE Dim_Product (
            product_id VARCHAR(100),
            product_name VARCHAR(255),
            category VARCHAR(100),
            sku VARCHAR(50),
            sku_status VARCHAR(50)
        );
    END

    -- ✅ Check if Dim_Customer table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Customer')
    BEGIN
        CREATE TABLE Dim_Customer (
            customer_id VARCHAR(100),
            customer_name VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(50),
            address VARCHAR(255),
            social_security_number VARCHAR(50),
            date_of_birth DATE,
            age INT,
            gender VARCHAR(10)
        );
    END

    -- ✅ Check if Dim_Date table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Date')
    BEGIN
        CREATE TABLE Dim_Date (
            date_key DATE,
            day_name VARCHAR(20),
            day_of_month INT,
            day_of_week INT,
            month INT,
            year INT,
            week_of_year INT
        );
    END

    -- ✅ Check if Dim_Store table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Store')
    BEGIN
        CREATE TABLE Dim_Store (
            store_id VARCHAR(100),
            store_name VARCHAR(255),
            address_line1 VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            country VARCHAR(100),
            postal_code VARCHAR(20),
            store_manager VARCHAR(255)
        );
    END

    -- ✅ Upsert Dim_Product
    UPDATE target_data
    SET
        target_data.product_name = source_data.product_name,
        target_data.category = source_data.category,
        target_data.sku = source_data.sku,
        target_data.sku_status = source_data.sku_status
    FROM Dim_Product AS target_data
    INNER JOIN Silver.Supply_Chain.Cleansed_product AS source_data
        ON target_data.product_id = source_data.product_id;

    INSERT INTO Dim_Product (product_id, product_name, category, sku, sku_status)
    SELECT DISTINCT product_id, product_name, category, sku, sku_status
    FROM Silver.Supply_Chain.Cleansed_product AS source_data
    WHERE NOT EXISTS (
        SELECT 1 FROM Dim_Product AS target_data WHERE target_data.product_id = source_data.product_id
    );

    -- ✅ Upsert Dim_Customer
    UPDATE target_data
    SET
        target_data.customer_name = source_data.customer_name,
        target_data.email = source_data.email,
        target_data.phone = source_data.phone,
        target_data.address = source_data.address,
        target_data.social_security_number = source_data.social_security_number,
        target_data.date_of_birth = source_data.date_of_birth,
        target_data.age = source_data.age,
        target_data.gender = source_data.gender
    FROM Dim_Customer AS target_data
    INNER JOIN Silver.Supply_Chain.Cleansed_customer AS source_data
        ON target_data.customer_id = source_data.customer_id;

    INSERT INTO Dim_Customer (customer_id, customer_name, email, phone, address, social_security_number, date_of_birth, age, gender)
    SELECT DISTINCT customer_id, customer_name, email, phone, address, social_security_number, date_of_birth, age, gender
    FROM Silver.Supply_Chain.Cleansed_customer AS source_data
    WHERE NOT EXISTS (
        SELECT 1 FROM Dim_Customer AS target_data WHERE target_data.customer_id = source_data.customer_id
    );

    -- ✅ Upsert Dim_Date
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
        ON target_data.date_key = CAST(source_data.sale_date AS DATE);

    INSERT INTO Dim_Date (date_key, day_name, day_of_month, day_of_week, month, year, week_of_year)
    SELECT DISTINCT CAST(sale_date AS DATE), DATENAME(WEEKDAY, sale_date), DAY(sale_date), DATEPART(WEEKDAY, sale_date), MONTH(sale_date), YEAR(sale_date), DATEPART(WEEK, sale_date)
    FROM Silver.Supply_Chain.Cleansed_sales AS source_data
    WHERE NOT EXISTS (
        SELECT 1 FROM Dim_Date AS target_data WHERE target_data.date_key = CAST(source_data.sale_date AS DATE)
    );

    -- ✅ Upsert Dim_Store
    UPDATE target_data
    SET
        target_data.store_name = source_data.store_name,
        target_data.address_line1 = source_data.address_line1,
        target_data.city = source_data.city,
        target_data.state = source_data.state,
        target_data.country = source_data.country,
        target_data.postal_code = source_data.postal_code,
        target_data.store_manager = source_data.store_manager
    FROM Dim_Store AS target_data
    INNER JOIN Silver.Supply_Chain.Cleansed_store AS source_data
        ON target_data.store_id = source_data.store_id;

    INSERT INTO Dim_Store (store_id, store_name, address_line1, city, state, country, postal_code, store_manager)
    SELECT store_id, store_name, address_line1, city, state, country, postal_code, store_manager
    FROM Silver.Supply_Chain.Cleansed_store AS source_data
    WHERE NOT EXISTS (
        SELECT 1 FROM Dim_Store AS target_data WHERE target_data.store_id = source_data.store_id
    );

END