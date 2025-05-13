CREATE PROC [salesforce_CRM].[LogPipelineAudit]
        @RunID VARCHAR(36),
    @PipelineName VARCHAR(255),
    @ActivityName VARCHAR(255),
    @Status VARCHAR(50),
    @StartTime DATETIME2(3),
    @EndTime DATETIME2(3),
    @DurationInSeconds INT,
    @ErrorDetails VARCHAR(255),
    @TriggeredBy VARCHAR(255),
    @PipelineRunTime DATETIME2(3)
AS
BEGIN
    INSERT INTO PipelineAuditLogs
    (RunID, PipelineName, ActivityName, Status, StartTime, EndTime, DurationInSeconds, ErrorDetails, TriggeredBy, PipelineRunTime)
    VALUES
    (@RunID, @PipelineName, @ActivityName, @Status, @StartTime, @EndTime, @DurationInSeconds, @ErrorDetails, @TriggeredBy, @PipelineRunTime);
END;