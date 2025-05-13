CREATE TABLE [salesforce_CRM].[Reconciliation_Report] (

	[TableName] varchar(100) NULL, 
	[MaxValue_Expected] datetime2(3) NULL, 
	[MaxValue_Actual] datetime2(3) NULL, 
	[BatchID_Expected] int NULL, 
	[BatchID_Actual] int NULL, 
	[MaxValue_Discrepancy] varchar(500) NULL, 
	[BatchID_Discrepancy] varchar(500) NULL, 
	[Rows_Inserted] int NULL, 
	[Rows_Updated] int NULL, 
	[RunTimestamp] datetime2(3) NULL
);