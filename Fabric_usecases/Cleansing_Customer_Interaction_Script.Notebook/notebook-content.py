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
from pyspark.sql.functions import col, lower, trim, regexp_replace, when, count, desc
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession.builder.appName("CustomerInteractionCleansing").getOrCreate()

#  Load the customer_interaction data in a DataFrame (df)
# Read data from Lakehouse table
df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_customer_interaction"
)

df.show(truncate=False)

# Step 1: Remove duplicates based on interaction_id
df = df.dropDuplicates(subset=["interaction_id"])


# Step 3: Clean URL parameters
# Remove URL parameters (e.g., /product/123?session_id=xyz)
df = df.withColumn("url", regexp_replace(col("url"), r"\?.*", ""))

# Step 4: Standardize event names (make them consistent - lower case)
df = df.withColumn("event_type", lower(trim(col("event_type"))))  # Convert to lowercase






# Show the cleaned data
df.show(truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col, lit, row_number, max as spark_max

# Load necessary dataframes


customer_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customerprofiles")
social_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_socialmedia")
email_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_email_campaign")
campaign_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign")

# Load the existing error table from Lakehouse
error_table = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details")

# Get the current max error_id
current_max_error_id = error_table.agg(spark_max("error_id").alias("max_error_id")).collect()[0]["max_error_id"]
if current_max_error_id is None:
    current_max_error_id = 0  # Start at 0 if the error table is empty

# Step 1: Validate Customer IDs
valid_customers = customer_df.select("customer_id").distinct()

# Identify invalid customer IDs
invalid_customers = df.join(
    valid_customers, on="customer_id", how="left_anti"
).select("customer_id").distinct()  # Select only distinct customer_ids


# Log invalid customer IDs to the error table
if invalid_customers.count() > 0:
    error_invalid_customers = invalid_customers.withColumn(
        "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
    ).select(
        col("error_id"),
        lit("Customer Interaction").alias("entity_name"),
        col("customer_id").alias("error_key"),
        lit("Customer ID not found in the customer.").alias("error_description"),
        F.current_timestamp().alias("created_date")
    )
    current_max_error_id += error_invalid_customers.count()  # Update the max error_id
    error_table = error_table.unionByName(error_invalid_customers)

# Remove invalid customer IDs from the cleansed DataFrame
df = df.join(
    invalid_customers.select("customer_id"), on="customer_id", how="left_anti"
)

# Step 2: Validate Campaign IDs (Social + Email + General Campaigns)
valid_campaigns = social_df.select("campaign_id").union(
    email_df.select("campaign_id")
).union(
    campaign_df.select("campaign_id")
).distinct()

# Identify invalid campaign IDs
invalid_campaigns = df.join(
    valid_campaigns, on="campaign_id", how="left_anti"
).select("campaign_id").distinct()

# Log invalid campaign IDs to the error table
if invalid_campaigns.count() > 0:
    error_invalid_campaigns = invalid_campaigns.withColumn(
        "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
    ).select(
        col("error_id"),
        lit("Customer Interaction").alias("entity_name"),
        col("campaign_id").alias("error_key"),
        lit("Invalid Campaign ID.").alias("error_description"),
        F.current_timestamp().alias("created_date")
    )
    current_max_error_id += error_invalid_campaigns.count()  # Update the max error_id
    error_table = error_table.unionByName(error_invalid_campaigns)

# Remove invalid campaign IDs from the cleansed DataFrame
df = df.join(
    invalid_campaigns.select("campaign_id"), on="campaign_id", how="left_anti"
)

# Show the final cleansed DataFrame
df.show()

# Show the updated error table
error_table.show()

# Define the output path or table name for your Delta table
output_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details"

# Save the error table as a Delta table
error_table.write.format("delta").mode("overwrite").save(output_path)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col, from_unixtime, to_date, current_date

# Get current date for comparison
current_date_col = F.current_date()  # Renamed to avoid confusion with the `current_date` function

# Convert BIGINT (Unix timestamp in milliseconds) to DATE
df_transformed = df.withColumn(
    "signup_date_converted",
    to_date(from_unixtime(col("signup_date") / 1000).cast("timestamp"))  # Divide by 1000 if in milliseconds
)

# Filter out records where signup_date is greater than the current date
df_filtered = df_transformed.filter(col("signup_date_converted") <= current_date_col)

# Drop the original `signup_date` column if it causes conflicts
df_filtered = df_filtered.drop("signup_date")

# Show filtered DataFrame
df_filtered.show()

# Define a mapping for event type order: click (1), view (2), purchase (3)
event_order_map = {
    'click': 1,
    'view': 2,
    'purchase': 3
}


# Define a UDF (User Defined Function) to map event types to their order
def event_order(event_type):
    return event_order_map.get(event_type.lower(), 0)

# Register the UDF
event_order_udf = F.udf(event_order)

# Add a column for the event order (numeric value)
df_with_order = df_filtered.withColumn("event_order", event_order_udf(F.col("event_type")))

# Define window specification for each customer, ordered by signup_date_converted
window_spec = Window.partitionBy("customer_id").orderBy("signup_date_converted")

# Create columns for previous values
df_with_lags = (
    df_with_order
    .withColumn("previous_signup_date", F.lag("signup_date_converted").over(window_spec))
    .withColumn("previous_signup_date", col("previous_signup_date").cast("date"))  # Ensure DateType
    .withColumn("previous_event_order", F.lag("event_order").over(window_spec))
    .withColumn("previous_event_type", F.lag("event_type").over(window_spec))
)

# Create a new column for timestamp and event sequence validation
df_with_validity = df_with_lags.withColumn(
    "validity", 
    F.when(F.col("previous_signup_date").isNull(), "valid")  # If it's the first record, mark as valid
     .when(F.col("signup_date_converted") >= F.col("previous_signup_date"), "valid")  # Check timestamp sequence
     .when(F.col("event_order") > F.col("previous_event_order"), "valid")  # Check event order (click -> view -> purchase)
     .when(
        (F.col("previous_event_type") == "purchase") & (F.col("event_type") == "view"), "valid"
     )  # Allow view after purchase, but ensure timestamp is valid
     .otherwise("invalid")  # Otherwise, mark as invalid
)

# Filter the data to keep only the valid records
df_valid_records = df_with_validity.filter(F.col("validity") == "valid")

df_valid_records = df_valid_records.withColumnRenamed("signup_date_converted", "signup_date").drop("validity")

# Show the final DataFrame

df_valid_records.show()

# Define the output path or table name for your Delta table
output_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customer_interaction"

# Save the DataFrame as a Delta table
df_valid_records.write.format("delta").mode("overwrite").save(output_path)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, from_unixtime, date_format, dayofmonth, dayofweek, month, year, weekofyear, to_date
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number


df_custint = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_customer_interaction"
)

# Convert signup_date to TIMESTAMP once
df_with_timestamp = df_custint.withColumn("signup_timestamp", from_unixtime(col("signup_date") / 1000))

# Use the converted TIMESTAMP for extracting date-related fields
dim_date = df_with_timestamp.select(
    to_date(col("signup_timestamp")).alias("signup_date"),  # Extract DATE
    date_format(col("signup_timestamp"), "EEEE").alias("day_name"),  # Day name
    dayofmonth(col("signup_timestamp")).alias("day_of_month"),  # Day of month
    dayofweek(col("signup_timestamp")).alias("day_of_week"),  # Day of week
    month(col("signup_timestamp")).alias("month"),  # Month number
    year(col("signup_timestamp")).alias("year"),  # Year
    weekofyear(col("signup_timestamp")).alias("week_of_year")  # Week number
).distinct()

# Add a date_key as a sequential number
window_spec = Window.orderBy("signup_date")
dim_date = dim_date.withColumn("date_key", row_number().over(window_spec))

# Reorder columns to make `date_key` the first column
dim_date = dim_date.select(
    "date_key",
    "signup_date",
    "day_name",
    "day_of_month",
    "day_of_week",
    "month",
    "year",
    "week_of_year"
)


dim_date.show()

dim_date.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Date")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, lit, when

cus_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customer_interaction")
df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Customer")
social_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_socialmedia")
email_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_email_campaign")
camp_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign")
df_date = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Date")

cus_df.show()

# Step 1: Join with demographic DataFrame to add customer_name
cus_df_with_name = cus_df.join(df.select("customer_id"), ["customer_id"], "left")


# Select only the common columns
social_common_df = social_df.select("campaign_id")
email_common_df = email_df.select("campaign_id")
camp_common_df = camp_df.select("campaign_id")

# Perform the union
all_campaigns_df = social_common_df.union(email_common_df).union(camp_common_df)

# Step 3: Join campaign details with cus_df_with_name to add campaign_name
cus_df_final = cus_df_with_name.join(all_campaigns_df, ["campaign_id"], "left")

# Display the final DataFrame with customer name and campaign name
cus_df_final.show(truncate=False)


# Join to map signup_date with date_key
fact_cus_interaction = cus_df_final.alias("cus") \
    .join(df_date.alias("date1"), col("cus.signup_date") == col("date1.signup_date"), "left") \
    .withColumn("signup_date_key", col("date1.date_key"))

# Join to map previous_signup_date with date_key
fact_cus_interaction = fact_cus_interaction.alias("cus") \
    .join(df_date.alias("date2"), col("cus.previous_signup_date") == col("date2.signup_date"), "left") \
    .withColumn("previous_signup_date_key", col("date2.date_key"))

# Replace null values in date keys with 0
fact_cus_interaction = fact_cus_interaction \
    .withColumn("signup_date_key", when(col("signup_date_key").isNull(), lit(0)).otherwise(col("signup_date_key"))) \
    .withColumn("previous_signup_date_key", when(col("previous_signup_date_key").isNull(), lit(0)).otherwise(col("previous_signup_date_key")))

# Drop original date columns if not needed
fact_cus_interaction = fact_cus_interaction.drop("signup_date", "date_key", "url", "previous_signup_date","event_type","previous_event_type", "day_name", "day_of_month", "day_of_week", "month", "year", "week_of_year")


# Show the result
fact_cus_interaction.show()




# Define the output path or table name for your Delta table
output_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Fact_CustomerJourney"

# Save the DataFrame as a Delta table
fact_cus_interaction.write.format("delta").mode("overwrite").save(output_path)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, when


# Assuming Spark Session
spark = SparkSession.builder.appName("Fact Website Logs").getOrCreate()


# Read the data
df_website = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_websitelogs")
df_date = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Date")


# Step 1: Convert `timestamp` in df_website to a date format to join with df_date
df_website_with_date = df_website.withColumn("signup_date", to_date(col("timestamp")))

# Step 2: Perform Left Join with df_date to get the timestamp_key
df_fact_website_logs = df_website_with_date.join(
    df_date,
    on="signup_date",  # Join on the date column
    how="left"
).select(
    col("user_id"),
    col("page_url"),
    col("session_duration"),
    col("source_id"),
    col("medium_id"),
    col("campaign_id"),
    when(col("date_key").isNotNull(), col("date_key")).otherwise(0).alias("timestamp_key")  # Default to 0 if no match
)


df_fact_website_logs.show()
df_fact_website_final = df_fact_website_logs.drop("source", "medium")
#To create dim_websitelogs table

df_fact_website_final.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Fact_WebsiteLogs")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, sum
from pyspark.sql import functions as F


# Group by campaign_id, source, and preferred_channel and calculate sum(total_spend)
cus_df_fact = cus_df_final.select("campaign_id", "source_id", "medium_id", "campaign_type_id", "total_spend") 

# Show the result
cus_df_fact.show(truncate=False)



# Define the output path or table name for your Delta table
output_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Fact_CampaignPerformance"

# Save the DataFrame as a Delta table
cus_df_fact.write.format("delta").mode("overwrite").save(output_path)




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
