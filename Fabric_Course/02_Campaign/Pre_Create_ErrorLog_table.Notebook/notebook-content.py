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
spark = SparkSession.builder.appName("LakehouseTable").getOrCreate()

# Define the table path
table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details"



# Define the schema for the error table
schema = StructType([
    StructField("error_id", IntegerType(), True),
    StructField("entity_name", StringType(), True),
    StructField("error_key", StringType(), True),
    StructField("error_description", StringType(), True),
    StructField("created_date", TimestampType(), True)
])

# Create an empty DataFrame using the schema
empty_df = spark.createDataFrame([], schema)

# Create a table in the Lakehouse or any target database
# Replace 'database_name' with the desired database and 'error_table' with the table name
empty_df.write.format("delta").mode("overwrite").save(table_path)

print("Empty table 'error_table' created successfully!")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
