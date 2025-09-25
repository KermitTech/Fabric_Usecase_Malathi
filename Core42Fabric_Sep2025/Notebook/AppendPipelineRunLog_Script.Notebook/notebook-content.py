# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# PARAMETERS CELL ********************



RunID = '102'
CurrentRunTime = "2023-03-31 00:00:12"
#CurrentRunTime = "2025-07-07T16:16:09.7551206Z"
PreviousRunTime = "2023-03-31 00:00:12"


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType,TimestampType

from notebookutils import mssparkutils

# ─── STEP 1: Get parameters from Fabric pipeline ───
#run_id = RunID
#current_str = CurrentRunTime
#previous_str = PreviousRunTime


schema = StructType([
    StructField("RunID", StringType(), True),
    StructField("CurrentRunTime", StringType(), False),
    StructField("PreviousRunTime", StringType(), True)  # nullable!
])

# ─── STEP 2: Parse timestamps safely ───

current_ts_str = CurrentRunTime.strip()
previous_ts_str = PreviousRunTime.strip().lower()

# Safety: Parse only if not "null"
previous_ts_clean = previous_ts_str if previous_ts_str not in ["null", "none", ""] else None

# ─── Step 2: Build raw data row ───
data = [(RunID, current_ts_str, previous_ts_clean)]


spark = SparkSession.builder.getOrCreate()
log_df = spark.createDataFrame(data, schema=schema)

# ─── STEP 4: Append to Lakehouse Delta table ───
log_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"

log_df.write.format("delta").mode("append").save(log_table_path)

print(f"✅ Logged run. RunID = {RunID}, Current = {current_ts_str}, Previous = {previous_ts_clean}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
