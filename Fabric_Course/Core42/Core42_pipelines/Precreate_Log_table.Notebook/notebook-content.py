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
from pyspark.sql.types import *

# Initialize Spark session
spark = SparkSession.builder.appName("GoldLoadLogInit").getOrCreate()

# Define the log table path (update this to your lakehouse path)
log_table_path = 'abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/gold/Load_Auditlogs'

# Define schema for the log table
log_schema = StructType([
    StructField("Timestamp", TimestampType(), True),
    StructField("Operation", StringType(), True),
    StructField("Status", StringType(), True),
    StructField("Bronze_Count", LongType(), True),
    StructField("Silver_Count", LongType(), True),
    StructField("Gold_Count", LongType(), True)
])

# Check if the Delta table already exists at the specified location
if not DeltaTable.isDeltaTable(spark, log_table_path):
    print("Log table doesn't exist — creating now.")
    
    # Create an empty DataFrame with schema
    empty_log_df = spark.createDataFrame([], log_schema)
    
    # Save as Delta table
    empty_log_df.write.format("delta").mode("overwrite").save(log_table_path)
    
    print("✅ Log table created successfully.")
else:
    print("✅ Log table already exists — skipping creation.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
