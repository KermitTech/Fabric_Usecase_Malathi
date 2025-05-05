# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Import necessary libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, concat_ws

# Initialize Spark session (Fabric automatically provides the Spark session)
spark = SparkSession.builder.getOrCreate()

# Define the file path in the Lakehouse
file_path = 'abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Files/Campaign/socialmedia_data.json'  # Replace with your file's path in Lakehouse

# Read the JSON file into a DataFrame
df = spark.read.option("multiline", "true").json(file_path)

# Explode and flatten the DataFrame
flattened_df = (
    df.select(explode(df["social_media_metrics"]).alias("metrics"))
      .select("metrics.*")
)

# Flatten the comments_content array into a single string
flattened_df = flattened_df.withColumn(
    "comments_content", concat_ws(", ", "comments_content")
)

# Show the DataFrame
flattened_df.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_socialmedia_data"  # Example of a table name

# Save the DataFrame as a Delta table
flattened_df.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
