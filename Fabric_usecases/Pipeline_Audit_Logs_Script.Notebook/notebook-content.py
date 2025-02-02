# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# PARAMETERS CELL ********************

PipelineRunId = "run-004"
PipelineId = "5edb08af-b64d-4b72-9080-89f2aeca3d7d"
PipelineName = "Test_Entry"  # As a string
StartTime = "2025-01-29 12:15:00"
EndTime = "2025-01-29 12:45:00"
WorkspaceId = "workspace-test01"
PipelineStatus = "TestStatus"
ErrorDescription = None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from delta.tables import DeltaTable
from pyspark.sql.functions import col, current_timestamp, lit, when

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Parameterized Pipeline Audit Logs Merge") \
    .getOrCreate()

# Sample input parameters
get_PipelineRunId = PipelineRunId
get_PipelineId = PipelineId
get_PipelineName = PipelineName  # As a string
get_StartTime = StartTime
get_EndTime = EndTime
get_WorkspaceId = WorkspaceId
get_PipelineStatus = PipelineStatus
get_ErrorDescription = ErrorDescription

# Create DataFrame with parameter values
#data = [(PipelineRunId, PipelineId, PipelineName, StartTime, EndTime, WorkspaceId, PipelineStatus, ErrorDescription)]

# Define schema for the DataFrame
pipelinelogs_schema = StructType([
    StructField("PipelineRunId", StringType(), True),
    StructField("PipelineId", StringType(), True),
    StructField("PipelineName", StringType(), True),  # Keep as String
    StructField("StartTime", StringType(), True),
    StructField("EndTime", StringType(), True),
    StructField("WorkspaceId", StringType(), True),
    StructField("PipelineStatus", StringType(), True),
    StructField("ErrorDescription", StringType(), True)
])



    # Prepare the new control entry with correct schema
data = [
        {
            "PipelineRunId": get_PipelineRunId,
            "PipelineId": get_PipelineId,
            "PipelineName": get_PipelineName,  # Ensure batch_id is passed earlier
            "StartTime": get_StartTime,  # Will be replaced by current_timestamp
            "EndTime": get_EndTime, # Adjust based on your logic
            "WorkspaceId": get_WorkspaceId,  # Ensure batch_id is passed earlier
            "PipelineStatus": get_PipelineStatus,  # Will be replaced by current_timestamp
            "ErrorDescription": get_ErrorDescription  # Adjust based on your logic
        }
    ]

# Create DataFrame
pipeline_logs_df = spark.createDataFrame(data, schema=pipelinelogs_schema)

print(pipeline_logs_df)

# Delta table path or name
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Salesforce_CRM/pipeline_audit_logs"

# Load the Delta table
delta_table = DeltaTable.forPath(spark, table_name)

# Perform the Merge operation
delta_table.alias("target").merge(
    pipeline_logs_df.alias("source"),
    "target.PipelineRunId = source.PipelineRunId"
).whenMatchedUpdate(set={
    "target.EndTime": "source.EndTime",
    "target.PipelineStatus": "source.PipelineStatus",
    "target.ErrorDescription": "source.ErrorDescription"
}).whenNotMatchedInsert(
    values={
    "target.PipelineRunId": "source.PipelineRunId",
    "target.PipelineId": "source.PipelineId",
    "target.PipelineName": "source.PipelineName",
    "target.StartTime": "source.StartTime",
    "target.EndTime": "source.EndTime",
    "target.WorkspaceId": "source.WorkspaceId",
    "target.PipelineStatus": "source.PipelineStatus",
    "target.ErrorDescription": "source.ErrorDescription"
    }
).execute()

print("Merge completed successfully!")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
