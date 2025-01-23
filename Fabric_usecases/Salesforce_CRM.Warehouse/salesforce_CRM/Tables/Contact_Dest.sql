CREATE TABLE [salesforce_CRM].[Contact_Dest] (

	[FirstName] varchar(100) NOT NULL, 
	[LastName] varchar(100) NOT NULL, 
	[AccountName] varchar(255) NULL, 
	[Title] varchar(100) NULL, 
	[LastActivityDate] datetime2(3) NULL, 
	[Email] varchar(255) NULL, 
	[Phone] varchar(20) NULL, 
	[Mobile] varchar(200) NULL, 
	[MailingState] varchar(100) NULL, 
	[MailingCountry] varchar(100) NULL, 
	[AccountOwner] varchar(100) NULL, 
	[CreatedDate] datetime2(3) NULL, 
	[updated_at] datetime2(3) NULL, 
	[batch_id] int NULL
);

