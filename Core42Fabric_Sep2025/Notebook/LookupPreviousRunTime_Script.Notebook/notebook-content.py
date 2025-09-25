# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from notebookutils import mssparkutils
from pyspark.sql.functions import date_format

spark = SparkSession.builder.getOrCreate()

# Define log table path
log_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"

# Load the table
df = spark.read.format("delta").load(log_table_path)

#df = df.withColumn("FormattedRunTime", date_format("CurrentRunTime", "M-d-yyyy h:mm:ss a"))


# Get the latest CurrentRunTime
latest_row = df.orderBy(df["CurrentRunTime"].desc()).limit(1).collect()

# Extract value or return null
previous_run_time = latest_row[0]["CurrentRunTime"] if latest_row else None

# Return the result so it can be accessed from pipeline
#dbutils.notebook.exit(str(previous_run_time) if previous_run_time else "null")
mssparkutils.notebook.exit(str(previous_run_time) if previous_run_time else "null")

print(previous_run_time)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
