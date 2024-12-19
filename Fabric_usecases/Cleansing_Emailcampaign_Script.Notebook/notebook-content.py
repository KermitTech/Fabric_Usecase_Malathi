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

# Read data from Lakehouse table
df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_email_campaign"
)

df.show(truncate=False)

# Step 1: Check if send_date is valid (convert to date, invalid dates will become null)
df = df.withColumn('send_date', F.to_date('send_date', 'yyyy-MM-dd'))

# Step 2: Replace null values in numeric fields with 0
numeric_columns = ['open_rate', 'click_rate', 'revenue', 'email_cost']
df = df.fillna({col: 0 for col in numeric_columns})

# Step 3: Ensure no negative values in opens, clicks, and conversions
df = df.withColumn('open_rate', F.when(F.col('open_rate') < 0, 0).otherwise(F.col('open_rate')))
df = df.withColumn('click_rate', F.when(F.col('click_rate') < 0, 0).otherwise(F.col('click_rate')))
#df = df.withColumn('conversions', F.when(F.col('conversions') < 0, 0).otherwise(F.col('conversions')))
df = df.withColumn('email_cost', F.when(F.col('email_cost') < 0, 0).otherwise(F.col('email_cost')))

# Regex to allow valid characters and punctuation
subject_regex = r"[^a-zA-Z0-9\s,'’\-]"

# Cleansing the email subject
df = df.withColumn(
    "email_subject",
    F.trim(F.regexp_replace(F.col("email_subject"), subject_regex, " "))  # Remove invalid characters
)

# Ensure email subject length is within the range (truncate or replace invalid lengths)
min_length, max_length = 10, 100
df = df.withColumn(
    "email_subject",
    F.when(F.length(F.col("email_subject")) < min_length, "Default Subject")  # Replace too short subjects
     .when(F.length(F.col("email_subject")) > max_length, F.expr(f"substring(email_subject, 1, {max_length})"))  # Truncate
     .otherwise(F.col("email_subject"))  # Keep as is if within range
)

# Step 5: Remove duplicate campaigns (based on campaign_id and send_date)
df = df.dropDuplicates(subset=['campaign_id', 'email_subject', 'send_date'])

df = df.withColumn(
    "valid_campaign",
    F.when(
        (df.send_date >= df.start_date) & (df.send_date <= df.end_date),
        "valid"
    ).otherwise("invalid")
)

df = df.filter(
    F.col("start_date").isNotNull())

df = df.filter(F.col("end_date").isNotNull())
df = df.filter(F.col("email_subject").isNotNull())
df = df.filter(F.col("send_date").isNotNull())


# Step 6: Remove exact duplicate rows
df = df.dropDuplicates()

# Show the cleansed DataFrame
df.show(truncate=False)


# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_email_campaign"  # Example of a table name

# Save the DataFrame as a Delta table
df.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, lit


# Read data

df_campaign = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_email_campaign")


df_campaign = df_campaign.withColumn(
    "CTOR", (col("click_rate") / col("open_rate")) * lit(100)
).withColumn(
    "ROI", (col("revenue") - col("email_cost")) / col("email_cost")
).withColumn(
    "Revenue_to_Cost_Ratio", col("revenue") / col("email_cost")
).withColumn(
    "CPE", col("email_cost") / (col("open_rate") + col("click_rate"))
).withColumn(
    "RPE", col("revenue") / (col("open_rate") + col("click_rate"))
)

df_campaign.show()
#To create dim_email_campaign table

df_campaign.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Email_Campaign")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
