CREATE PROCEDURE [salesforce_CRM].[Contact_Syn_INSUPD]
    @batch_id INT -- Parameter to pass the batch ID
AS
BEGIN
    BEGIN TRY
        -- Check if [salesforce_CRM].[Contact_Updated] has any rows
        IF EXISTS (SELECT 1 FROM [salesforce_CRM].[Contact_Updated])
        BEGIN
            -- Perform the update for matching records
            UPDATE target
            SET target.Mobile = source.Email,
                target.Phone = source.Phone,
                target.Email = source.Email,
                target.LastActivityDate = source.LastActivityDate,
                target.CreatedDate = '2025-01-22T13:15:57',
                target.LoadType = 'UPDATE' -- Mark as an UPDATE
            FROM [salesforce_CRM].[Contact] AS target
            INNER JOIN [salesforce_CRM].[Contact_Updated] AS source
            ON target.FirstName = source.FirstName
               AND target.LastName = source.LastName
               AND target.AccountName = source.AccountName;

            PRINT 'Matching records updated successfully.';

            -- Perform the insert for non-matching records and capture the row count
            DECLARE @insert_count INT;

            INSERT INTO [salesforce_CRM].[Contact] 
                (FirstName, LastName, AccountName, Mobile, Phone, Email, LastActivityDate, CreatedDate, batch_id, LoadType)
            SELECT 
                source.FirstName, 
                source.LastName, 
                source.AccountName, 
                source.Mobile, 
                source.Phone, 
                source.Email, 
                source.LastActivityDate, 
                GETDATE(), -- Insert the current timestamp for CreatedDate
                @batch_id, -- Insert the provided batch ID
                'INSERT' -- Mark as an INSERT
            FROM [salesforce_CRM].[Contact_Updated] AS source
            LEFT JOIN [salesforce_CRM].[Contact] AS target
            ON target.FirstName = source.FirstName
               AND target.LastName = source.LastName
               AND target.AccountName = source.AccountName
            WHERE target.FirstName IS NULL;

            -- Capture the number of rows inserted
            SET @insert_count = @@ROWCOUNT;

            PRINT CONCAT(@insert_count, ' new records inserted.');

            -- Empty the [salesforce_CRM].[Contact_Updated] table while retaining the schema
            TRUNCATE TABLE [salesforce_CRM].[Contact_Updated];

            PRINT 'Sync operation completed successfully, and Contact_Updated table has been emptied.';

            -- If inserts occurred, calculate the maximum CreatedDate and update ControlTable
            IF @insert_count > 0
            BEGIN
                DECLARE @max_value DATETIME2(3) = (SELECT MAX(CreatedDate) FROM [salesforce_CRM].[Contact]);

                UPDATE [salesforce_CRM].[ControlTable]
                SET MaxValue = @max_value,
                    BatchValue = @batch_id,
                    LastUpdated = GETDATE()
                WHERE TableName = 'Contact';

                PRINT 'Control table updated successfully with new MaxValue and BatchValue.';
            END
            ELSE
            BEGIN
                PRINT 'No new records inserted. Control table not updated.';
            END
        END
        ELSE
        BEGIN
            PRINT 'No records found in [salesforce_CRM].[Contact_Updated]. Skipping sync operation.';
        END
    END TRY
    BEGIN CATCH
        -- Handle any errors that occur
        PRINT 'An error occurred during the sync process.';
        THROW;
    END CATCH
END;