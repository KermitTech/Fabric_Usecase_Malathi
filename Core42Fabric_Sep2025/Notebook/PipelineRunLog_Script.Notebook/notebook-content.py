# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c",
# META       "default_lakehouse_name": "Core42",
# META       "default_lakehouse_workspace_id": "0954d773-1b76-4837-90bb-56305401112a",
# META       "known_lakehouses": [
# META         {
# META           "id": "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Initialize Spark session
spark = SparkSession.builder.appName("PipelineRunLogInit").getOrCreate()

# Define the log table path
run_log_table_path = 'abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog'

# Define schema for the run log table
run_log_schema = StructType([
    StructField("RunID", StringType(), True),  # Optional, can be used for ordering
    StructField("CurrentRunTime", StringType(), True),
    StructField("PreviousRunTime", StringType(), True)
])

# Check if the Delta table already exists at the specified location
if not DeltaTable.isDeltaTable(spark, run_log_table_path):
    print("Run log table doesn't exist — creating now.")
    
    # Create an empty DataFrame with schema
    empty_run_log_df = spark.createDataFrame([], run_log_schema)
    
    # Save as Delta table
    empty_run_log_df.write.format("delta").mode("overwrite").save(run_log_table_path)
    
    print("PipelineRunLog table created successfully.")
else:
    print("PipelineRunLog table already exists — skipping creation.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
