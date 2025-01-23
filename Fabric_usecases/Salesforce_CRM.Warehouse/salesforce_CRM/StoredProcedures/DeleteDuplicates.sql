-- DELETE Old Records To Update

CREATE PROC [salesforce_CRM].[DeleteDuplicates]

AS 

BEGIN 


--DROP table [Salesforce_CRM].[salesforce_CRM].[TempTable];

-- Step 1: Insert the rows to keep into a temporary table 

SELECT * 

INTO [Salesforce_CRM].[salesforce_CRM].[TempTable]

FROM ( 

SELECT *, ROW_NUMBER() OVER (PARTITION BY FirstName, LastName, [AccountName] ORDER BY LastActivityDate DESC) AS row_num 

FROM [Salesforce_CRM].[salesforce_CRM].[Contact] 

) AS ranked_rows 

WHERE row_num = 1; 

-- Step 2: Truncate the original table 

DELETE FROM [Salesforce_CRM].[salesforce_CRM].[Contact]; 

 

-- Step 3: Insert back the deduplicated data 

INSERT INTO [Salesforce_CRM].[salesforce_CRM].[Contact] 

SELECT 
    FirstName, 
    LastName, 
    AccountName, 
    Title, 
    LastActivityDate, 
    Email, 
    Phone, 
    Mobile, 
    MailingState, 
    MailingCountry, 
    AccountOwner, 
    CreatedDate
     FROM [Salesforce_CRM].[salesforce_CRM].[TempTable]; 

 

-- Step 4: Drop the temporary table 

DROP TABLE [Salesforce_CRM].[salesforce_CRM].[TempTable]; 

END;