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
from pyspark.sql.functions import col, lit, from_unixtime, current_date, when, row_number
from pyspark.sql.window import Window
from pyspark.sql import SparkSession


# Create a Spark session
spark = SparkSession.builder.appName("CampaignDataCleansing").getOrCreate()

# Read data from Lakehouse table
campaign_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_campaign"
)

# Load the existing error table from Lakehouse
error_table = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details"
)

# Get the current max error_id
current_max_error_id = error_table.agg(F.max("error_id").alias("max_error_id")).collect()[0]["max_error_id"]
if current_max_error_id is None:
    current_max_error_id = 0  # Start at 0 if the error table is empty


def clean_campaign_data_with_error_logging(df, error_table, current_max_error_id):

    df = df.filter(col("campaign_name").isNotNull())

    # Step 1: Replace underscores with spaces
    df = df.withColumn('campaign_name', F.regexp_replace('campaign_name', '_', ' '))
    
    # Step 2: Standardize campaign names (remove special characters)
    cleansed_df = df.withColumn(
        'campaign_name_cleaned', 
        F.regexp_replace('campaign_name', '[^a-zA-Z0-9\\s-]', '')
    )
    
    # Identify invalid campaign names (if cleaning resulted in an empty string)
    invalid_campaigns = cleansed_df.filter(cleansed_df.campaign_name_cleaned == "")

    

    # Log invalid campaign names to error table
    if invalid_campaigns.count() > 0:
        error_invalid_names = invalid_campaigns.withColumn(
            "error_id", 
            row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
        ).select(
            col("error_id"),
            lit("campaign").alias("entity_name"),
            col("campaign_id").alias("error_key"),
            lit("Invalid campaign name after cleansing.").alias("error_description"),
            F.current_timestamp().alias("created_date")
        )
        current_max_error_id += error_invalid_names.count()  # Update max error_id
        error_table = error_table.unionByName(error_invalid_names)
    
    # Keep only valid campaign names
    cleansed_df = cleansed_df.filter(cleansed_df.campaign_name_cleaned != "")
    


    # Validate Campaign IDs (check if campaign_id is not null)

    invalid_campaign_ids = df.filter(col("campaign_id").isNull())
    
    # Log invalid campaign IDs to the error table
    if invalid_campaign_ids.count() > 0:
        error_invalid_campaign_ids = invalid_campaign_ids.withColumn(
            "error_id", 
            row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
        ).select(
            col("error_id"),
            lit("campaign").alias("entity_name"),
            col("campaign_id").alias("error_key"),
            lit("Invalid campaign ID: cannot be null.").alias("error_description"),
            F.current_timestamp().alias("created_date")
        )
        # Update the max error_id
        current_max_error_id += error_invalid_campaign_ids.count()
        error_table = error_table.unionByName(error_invalid_campaign_ids)
    
    # Remove invalid campaign IDs from the cleansed DataFrame
    cleansed_df = df.filter(col("campaign_id").isNotNull())

    
    # Step 3: Compute the 99th percentile for campaign_cost
    campaign_cost_percentile = cleansed_df.approxQuantile("campaign_cost", [0.99], 0.05)[0]
    
    # Handle cost outliers
    cleansed_df = cleansed_df.withColumn(
        'campaign_cost_cleaned',
        when(col('campaign_cost') > campaign_cost_percentile,
             lit(campaign_cost_percentile))  # Replace with 99th percentile value
        .otherwise(col('campaign_cost'))  # Keep original cost if not an outlier
    )
    
    # Identify outlier records
    outlier_records = cleansed_df.filter(col('campaign_cost') > campaign_cost_percentile)
    
    # Log outliers to error table
    if outlier_records.count() > 0:
        error_outliers = outlier_records.withColumn(
            "error_id", 
            row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
        ).select(
            col("error_id"),
            lit("campaign").alias("entity_name"),
            col("campaign_id").alias("error_key"),
            F.concat(
                lit("Campaign cost exceeds 99th percentile ("),
                lit(campaign_cost_percentile),
                lit(").")
            ).alias("error_description"),
            F.current_timestamp().alias("created_date")
        )
        current_max_error_id += error_outliers.count()  # Update max error_id
        error_table = error_table.unionByName(error_outliers)
    
    # Final cleansed dataset
    cleansed_df = cleansed_df.drop("campaign_name_cleaned").drop("campaign_cost_cleaned")
    
    # Convert from milliseconds to date if the columns are in LongType or TimestampType
    cleansed_df = cleansed_df \
        .withColumn("start_date", from_unixtime(col("start_date") / 1000).cast("date")) \
        .withColumn("end_date", from_unixtime(col("end_date") / 1000).cast("date"))
    
    return cleansed_df, error_table, current_max_error_id


# Run the cleansing function
cleansed_df, error_table, current_max_error_id = clean_campaign_data_with_error_logging(
    campaign_df, error_table, current_max_error_id
)

# Show results
cleansed_df.show(truncate=False)
error_table.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign"  # Example of a table name
error_table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details"  # Example of a table name

# Save the DataFrame as a Delta table
cleansed_df.write.format("delta").mode("overwrite").save(table_name)
error_table.write.format("delta").mode("overwrite").save(error_table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


from pyspark.sql.functions import col,round


# Load cleansed Silver Layer tables

df_campaign = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign")


# Calculate multiple metrics at once
df_campaign = df_campaign \
    .withColumn("conversion_rate", round((col("conversions") / col("clicks")) * 100, 2)) \
    .withColumn("CTR", round((col("clicks") / col("impressions")) * 100, 2)) \
    .withColumn("CPC", round(col("campaign_cost") / col("clicks"), 2)) \
    .withColumn("CPA", round(col("campaign_cost") / col("conversions"), 2)) \
    .withColumn("ROAS", round(col("revenue") / col("campaign_cost"), 2)) \
    .withColumn("ROI", round((col("revenue") - col("campaign_cost")) / col("campaign_cost") * 100, 2)) \
    .withColumn("CES", round((col("conversion_rate") * 0.4) + (col("ctr") * 0.3) + (col("roas") * 0.3), 2))



df_campaign.show()



#To create dim_customer table

df_campaign.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Campaign")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
