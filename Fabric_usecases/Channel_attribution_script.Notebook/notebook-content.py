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
from pyspark.sql.window import Window


# Read data from Lakehouse table
df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customer_interaction"
)

df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Define window specifications
window_spec = Window.partitionBy("customer_id", "campaign_id", "source_id").orderBy("signup_date")
global_touches_window = Window.partitionBy("campaign_id", "source")

# Add touch position and total touches per customer
df_with_position = df.withColumn(
    "touch_position", F.row_number().over(window_spec)
)

# Calculate the total number of touchpoints per customer based on the campaign_id and source (still at the customer level)
df_with_position = df_with_position.withColumn(
    "total_touches", F.count("*").over(Window.partitionBy("customer_id", "campaign_id", "source_id"))
)

df_with_position.show()

# Add conversion flag (purchase = 1, otherwise = 0)
df_with_position = df_with_position.withColumn(
    "is_conversion", F.when(F.col("event_type") == "purchase", 1).otherwise(0)
)

# Compute first-touch and last-touch attribution logic
df_with_position = df_with_position.withColumn(
    "global_first_touch_attributions",
    F.when(F.col("touch_position") == 1, 1).otherwise(0)
).withColumn(
    "global_last_touch_attributions",
    F.when(F.col("touch_position") == F.col("total_touches"), 1).otherwise(0)
)

# Calculate the linear attribution value based on the total touches
df_with_position = df_with_position.withColumn(
    "linear_attribution_value", 1.0 / F.col("total_touches")
)



# Group by campaign, source, and touch position to aggregate the data
df_attribution = df_with_position.groupBy(
    "customer_id", "campaign_id",  "source_id", "touch_position", "is_conversion"
).agg(
    F.max("global_first_touch_attributions").alias("first_touch_attributions"),
    F.max("global_last_touch_attributions").alias("last_touch_attributions"),
    F.sum("linear_attribution_value").alias("linear_attribution_value"),
    F.max("total_touches").alias("total_touches")
)

# Sort the final result
df_attribution_sorted = df_attribution.orderBy(
    F.col("customer_id").asc(),
    F.col("campaign_id").asc(),
    F.col("source_id").asc(),
    F.col("touch_position").asc()
)

# Show the results
df_attribution_sorted.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Fact_Channel_Attribution"  # Example of a table name

# Save the DataFrame as a Delta table
df_attribution_sorted.write.format("delta").mode("overwrite").save(table_name)



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F


# Read data from Lakehouse table
channel_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Fact_Channel_Attribution"
)

# Query 1: Maximum purchased count where is_conversion = 1
max_purchased = (
    channel_df.filter((F.col("is_conversion") == 1))
    .groupBy("campaign_id", "source_id")
    .agg(F.count("is_conversion").alias("Purchased_count"))
    .orderBy(F.desc("Purchased_count"))
)

# Query 2: Maximum Last Touch Attributions where is_conversion = 1
max_last_touch_attributions = (
    channel_df.filter((F.col("last_touch_attributions") == 1))
    .groupBy("campaign_id", "source_id")
    .agg(F.count("last_touch_attributions").alias("last_touch_count"))
    .orderBy(F.desc("last_touch_count"))
)


# Show the result for Query 1
print("Query 1: Maximum Last Touch Attributions")
max_purchased.show(truncate=False)
max_last_touch_attributions.show()
# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/RPT_WinningCampaigns"  # Example of a table name

# Save the DataFrame as a Delta table
max_purchased.write.format("delta").mode("overwrite").save(table_name)


# Query 2: Maximum First Touch Attributions
max_first_touch_attributions = (
    channel_df.filter((F.col("first_touch_attributions") == 1))
    .groupBy("campaign_id", "source_id")
    .agg(F.count("first_touch_attributions").alias("first_touch_count"))
    .orderBy(F.desc("first_touch_count"))
)

# Show the result for Query 2
print("Query 2: Maximum First Touch Attributions")
max_first_touch_attributions.show(truncate=False)



# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/RPT_Customer_Engagement_Campaigns"  # Example of a table name

# Save the DataFrame as a Delta table
max_first_touch_attributions.write.format("delta").mode("overwrite").save(table_name)


combined_touch = (
    channel_df.groupBy("campaign_id", "source_id")
    .agg(
        F.sum("first_touch_attributions").alias("first_touch_count"),
        F.sum("last_touch_attributions").alias("last_touch_count"),
         F.sum("is_conversion").alias("purchased_count")
    )
    .orderBy(F.desc("last_touch_count"), F.desc("first_touch_count"))
)
combined_touch.show(truncate=False)




# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/RPT_Campaign_Touch_Analysis"  # Example of a table name

# Save the DataFrame as a Delta table
combined_touch.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
