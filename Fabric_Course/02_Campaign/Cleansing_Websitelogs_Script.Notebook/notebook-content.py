# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql import functions as F

# Load campaign data from the Lakehouse table
campaign_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_campaign"
)
valid_campaign_ids = campaign_df.select("campaign_id").distinct()

valid_campaign_ids.show()

# Read data from Lakehouse table
logs_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_websitelogs"
)


# Validate campaign_id against the campaign data
df = logs_df.join(
    valid_campaign_ids,
    on="campaign_id",
    how="inner"  # Retain only rows with valid campaign IDs
)

# Alternatively, use a filter approach
# valid_campaign_ids_list = [row["campaign_id"] for row in valid_campaign_ids.collect()]
# cleaned_logs_df = logs_df.filter(F.col("campaign_id").isin(valid_campaign_ids_list))

# Show the cleansed data
df.show(truncate=False)





# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F

valid_sources = ["google", "facebook", "instagram", "linkedin"]

# Define the expected date format
expected_date_format = "yyyy-MM-dd'T'HH:mm:ss"

# Cleansing Steps with Date Validation
df_cleaned = (
    df
    # Step 1: Remove rows with null user_id
    .filter(F.col("user_id").isNotNull())
    
    # Step 2: Replace null page_url with "unknown"
    .withColumn("page_url", F.when(F.col("page_url").isNull(), "unknown").otherwise(F.col("page_url")))
    
    # Step 3: Standardize source and device fields to lowercase
    .withColumn("source", F.lower(F.col("source")))
    .withColumn("medium", F.lower(F.col("medium")))
    
    # Step 5: Validate source and device
    .filter(F.col("source").isin(valid_sources))
    
    # Step 6: Validate timestamp format
    .withColumn("timestamp_valid", F.to_timestamp(F.col("timestamp"), expected_date_format).isNotNull())
    .filter(F.col("timestamp_valid"))  # Only keep rows with valid timestamp
    
    # Step 7: Remove duplicates
    .dropDuplicates()
)

# Drop intermediate validation column if needed
df_cleaned = df_cleaned.drop("timestamp_valid")

# Show the cleansed data
df_cleaned.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_websitelogs"  # Example of a table name

# Save the DataFrame as a Delta table
df.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
