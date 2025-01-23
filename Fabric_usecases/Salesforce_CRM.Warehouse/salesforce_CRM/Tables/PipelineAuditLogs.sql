CREATE TABLE [salesforce_CRM].[PipelineAuditLogs] (

	[RunID] varchar(36) NOT NULL, 
	[PipelineName] varchar(255) NULL, 
	[ActivityName] varchar(255) NULL, 
	[Status] varchar(50) NULL, 
	[StartTime] datetime2(3) NULL, 
	[EndTime] datetime2(3) NULL, 
	[DurationInSeconds] int NULL, 
	[ErrorDetails] varchar(255) NULL, 
	[TriggeredBy] varchar(255) NULL, 
	[PipelineRunTime] datetime2(3) NULL
);

