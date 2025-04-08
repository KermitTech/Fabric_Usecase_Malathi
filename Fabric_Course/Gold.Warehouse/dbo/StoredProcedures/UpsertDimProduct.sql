CREATE PROCEDURE dbo.UpsertDimProduct
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if Dim_Product table exists; if not, create it
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

    -- Update existing records
    UPDATE target_data
    SET
        target_data.product_name = source_data.product_name,
        target_data.category = source_data.category,
        target_data.sku = source_data.sku,
        target_data.sku_status = source_data.sku_status
    FROM Dim_Product AS target_data
    INNER JOIN Silver.Supply_Chain.Cleansed_product AS source_data
        ON target_data.product_id = source_data.product_id;

    -- Insert new records
    INSERT INTO Dim_Product (product_id, product_name, category, sku, sku_status)
    SELECT DISTINCT
        product_id,
        product_name,
        category,
        sku,
        sku_status
    FROM Silver.Supply_Chain.Cleansed_product AS source_data
    WHERE NOT EXISTS (
        SELECT 1
        FROM Dim_Product AS target_data
        WHERE target_data.product_id = source_data.product_id
    );
END