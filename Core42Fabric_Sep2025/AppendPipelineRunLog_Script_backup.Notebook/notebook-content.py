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
#CurrentRunTime = "2023-03-31 00:00:12"
CurrentRunTime = "2025-07-07T16:16:09.7551206Z"
PreviousRunTime = "2025-07-07T16:16:09.7551206Z"


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
    StructField("CurrentRunTime", TimestampType(), False),
    StructField("PreviousRunTime", TimestampType(), True)  # nullable!
])

# ─── STEP 2: Parse timestamps safely ───

def clean_iso_timestamp(ts: str) -> str:
    ts = ts.rstrip('Z')
    if '.' in ts:
        date_part, frac_part = ts.split('.', 1)
        frac_part = frac_part[:6]  # truncate to 6 digits max
        ts = f"{date_part}.{frac_part}"
    return ts

# Clean and parse current run time
clean_curr_ts = clean_iso_timestamp(CurrentRunTime)
pipeline_time = datetime.strptime(clean_curr_ts, "%Y-%m-%d %H:%M:%S.%f")

# Clean and parse previous run time
clean_prev_ts = clean_iso_timestamp(PreviousRunTime)
previous_run_dt = datetime.strptime(clean_prev_ts, "%Y-%m-%dT%H:%M:%S.%f")

current_ts = datetime.fromisoformat(CurrentRunTime)
previous_ts = None if PreviousRunTime in [None, "", "null"] else datetime.fromisoformat(PreviousRunTime)

# ─── STEP 3: Create DataFrame ───
data = [(RunID, pipeline_time, previous_run_dt)]
#columns = ["RunID", "CurrentRunTime", "PreviousRunTime"]

spark = SparkSession.builder.getOrCreate()
log_df = spark.createDataFrame(data, schema=schema)

# ─── STEP 4: Append to Lakehouse Delta table ───
log_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"

log_df.write.format("delta").mode("append").save(log_table_path)

print(f"✅ Logged run. RunID = {RunID}, Current = {pipeline_time}, Previous = {previous_run_dt}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
