CREATE PROCEDURE dbo.UpsertDimStore
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if Dim_Store table exists; if not, create it
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dim_Store')
    BEGIN
        CREATE TABLE Dim_Store (
            store_id varchar(100),
            store_name VARCHAR(255),
            address_line1 VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            country VARCHAR(100),
            postal_code VARCHAR(20),
            store_manager VARCHAR(255)
        );
    END

    -- Update existing records
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

    -- Insert new records
    INSERT INTO Dim_Store (store_id, store_name, address_line1, city, state, country, postal_code, store_manager)
    SELECT
        store_id,
        store_name,
        address_line1,
        city,
        state,
        country,
        postal_code,
        store_manager
    FROM Silver.Supply_Chain.Cleansed_store AS source_data
    WHERE NOT EXISTS (
        SELECT 1
        FROM Dim_Store AS target_data
        WHERE target_data.store_id = source_data.store_id
    );
END