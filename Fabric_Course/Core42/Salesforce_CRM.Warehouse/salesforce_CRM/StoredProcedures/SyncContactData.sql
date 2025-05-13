CREATE PROCEDURE [salesforce_CRM].[SyncContactData]
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
                target.CreatedDate = '2025-01-22T13:15:57'
            FROM [salesforce_CRM].[Contact] AS target
            INNER JOIN [salesforce_CRM].[Contact_Updated] AS source
            ON target.FirstName = source.FirstName
               AND target.LastName = source.LastName
               AND target.AccountName = source.AccountName;

            PRINT 'Matching records updated successfully.';

            -- Perform the insert for non-matching records
          --  INSERT INTO [salesforce_CRM].[Contact] (FirstName, LastName, AccountName, Mobile, Phone, Email, LastActivity, Updated_At)
           -- SELECT source.FirstName, source.LastName, source.AccountName, source.Mobile, source.Phone, source.Email, source.LastActivity, source.Updated_At
          --  FROM [salesforce_CRM].[Contact_Updated] AS source
          --  LEFT JOIN [salesforce_CRM].[Contact] AS target
          --  ON target.FirstName = source.FirstName
          --     AND target.LastName = source.LastName
           --    AND target.AccountName = source.AccountName
          --  WHERE target.FirstName IS NULL;

           -- PRINT 'New records inserted successfully.';

            -- Empty the [salesforce_CRM].[Contact_Updated] table while retaining the schema
            TRUNCATE TABLE [salesforce_CRM].[Contact_Updated];

            PRINT 'Sync operation completed successfully, and Contact_Updated table has been emptied.';
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