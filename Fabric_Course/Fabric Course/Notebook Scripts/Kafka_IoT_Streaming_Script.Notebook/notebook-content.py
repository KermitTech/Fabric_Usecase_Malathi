# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, from_unixtime
import time

# Initialize the Spark session
spark = SparkSession.builder \
    .appName("IoT Stream Example") \
    .getOrCreate()



# Read the sales_transactions.csv into a Spark DataFrame
iot_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/IoT_data"
)
iot_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


 # Convert from milliseconds to date if the columns are in LongType or TimestampType
iot_df = iot_df \
    .withColumn("Timestamp", from_unixtime(col("Timestamp") / 1000).cast("date"))

iot_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
import time

# Initialize the Spark session
spark = SparkSession.builder \
    .appName("IoT Stream Example") \
    .getOrCreate()

# Kafka configuration
kafka_bootstrap_servers = "34.51.128.134:9092"  # Replace with your Kafka broker addresses
kafka_topic = "productIoTData"  # Replace with your Kafka topic name

# Define the schema of your IoT JSON data
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

iot_schema = StructType([
    StructField("ProductID", IntegerType(), True),
    StructField("StoreID", IntegerType(), True),
    StructField("Temperature", DoubleType(), True),
    StructField("Humidity", DoubleType(), True),
    StructField("Timestamp", TimestampType(), True)
])

# Create a streaming DataFrame that reads data from Kafka topic
iot_stream_df = spark.readStream \
 .format("kafka") \
 .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
 .option("subscribe", kafka_topic) \
 .option("startingOffsets", "Earliest") \
 .option("group.id", "streamsetsDataCollector") \
 .load()

# Kafka messages are in binary format (key and value), so we'll convert the 'value' column to a string
iot_json_df = iot_stream_df.selectExpr("CAST(value AS STRING) as json_value")

# Parse the JSON 'value' field according to the schema
iot_data_df = iot_json_df.select(from_json(col("json_value"), iot_schema).alias("data")).select("data.*")

# Example: Select the relevant fields and perform any additional transformations
iot_data_df = iot_data_df.withColumn("EventDate", col("Timestamp").cast("date"))

# Show the first few records (for testing purposes)




iot_data_df \
  .withColumn("bodyAsString", f.col("body").cast("string")) \
  .select(f.from_json(f.col("bodyAsString"), Schema).alias("events")) \
  .select("events.*") \
  .writeStream \
  .format("delta") \
  .option("checkpointLocation", "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain") \
  .outputMode("append") \
  .toTable("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/IoT_data")  # Write to the Delta table (assuming you have this table in your Lakehouse)







# Stop the stream
query.stop()

print("Stream stopped.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import time
time.sleep(5)  # Let the stream process for 5 seconds (just for demo purposes)

# Stop the stream
query.stop()

print("Stream stopped.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

query.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
