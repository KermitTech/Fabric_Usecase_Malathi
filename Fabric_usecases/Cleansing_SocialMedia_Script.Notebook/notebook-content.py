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
from pyspark.sql.functions import udf, from_unixtime
from pyspark.sql.functions import col, split, substring, explode, regexp_replace, regexp_extract, upper, lower, trim, length
from pyspark.sql.types import StringType
from pyspark.sql import functions as F

# Initialize Spark session
spark = SparkSession.builder.appName("SocialMediaComments").getOrCreate()

# Read data from Lakehouse table
data = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_socialmedia_data"
)
data.show(truncate=False)
# Step 1: Split the comments_content column into arrays and explode into separate rows



exploded_data = (
    data.withColumn("comment", explode(split(trim(col("comment_text")), r"\s*,\s*")))  # Split using ';' as delimiter
    .withColumn("comment", trim(col("comment")))  # Remove leading and trailing spaces from each comment
    .drop("comment_text")  # Drop the original comments_content column
)

# Step 2: Remove emojis from the comments
def remove_emojis(text):
    # Emoji regex pattern to match Unicode emojis
    emoji_pattern = (
        r"[\x{1F600}-\x{1F64F}"  # Emoticons
        r"\x{1F300}-\x{1F5FF}"  # Symbols & pictographs
        r"\x{1F680}-\x{1F6FF}"  # Transport & map symbols
        r"\x{1F1E0}-\x{1F1FF}"  # Flags
        r"\x{2700}-\x{27BF}"    # Dingbats
        r"\x{2600}-\x{26FF}"    # Miscellaneous symbols
        r"]+"  # Match one or more emojis
    )

    # Retain only alphanumeric characters, spaces, hashtags (#), and mentions (@)
    return regexp_replace(text, emoji_pattern, "")

cleaned_data = exploded_data.withColumn("cleaned_comment", remove_emojis(col("comment")))

# Step 3: Filter out irrelevant data (e.g., too short comments or generic phrases)
filtered_data = cleaned_data.filter(
    (col("cleaned_comment").rlike("[a-zA-Z0-9@#]")) &  # Ensure the comment has at least some valid content
    (length(col("cleaned_comment")) > 4)              # Remove very short comments (adjust threshold as needed)
)

# Step 4: Remove known spam patterns (you can expand this list)
spam_patterns = ["buy now", "click here", "subscribe", "win big", "Can't wait"]

#for pattern in spam_patterns:
#    filtered_data = filtered_data.filter(~lower(col("cleaned_comment")).contains(pattern))


# Create a single regex pattern to match any of the spam patterns
spam_regex = "|".join([f"(?i){pattern}" for pattern in spam_patterns])  # (?i) makes the pattern case-insensitive

# Filter rows where cleaned_comment does not match the spam regex
filtered_data = filtered_data.filter(~col("cleaned_comment").rlike(spam_regex))


# Step 3: Extract hashtags and mentions
result_data = filtered_data.withColumn(
    "hashtags", regexp_extract(col("comment"), r"(#[\w]+)", 0)
).withColumn(
    "mentions", regexp_extract(col("comment"), r"(@[\w]+)", 0)
)

# Step 4: Remove hashtags and mentions from the comment
result_data = result_data.withColumn(
    "cleaned_comment", regexp_replace(col("cleaned_comment"), r"(@[\w]+|#[\w]+)", "")  # Remove hashtags and mentions
).withColumn(
    "cleaned_comment", trim(col("cleaned_comment"))  # Trim extra spaces after removal
)

result_data = result_data.withColumn("cleaned_comment", regexp_replace(col("cleaned_comment"), r"[^\w\s@#]", ""))

 # Convert from milliseconds to date if the columns are in LongType or TimestampType
result_data = result_data \
    .withColumn("start_date", from_unixtime(col("start_date") / 1000).cast("date")) \
    .withColumn("end_date", from_unixtime(col("end_date") / 1000).cast("date"))

# Step 4: Select only necessary columns
#final_data = result_data.select("platform", "campaign_id", "comment", "cleaned_comment", "hashtags", "mentions")

final_data = result_data.drop("comment")

# Show the result
final_data.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_socialmedia"  # Example of a table name

# Save the DataFrame as a Delta table
final_data.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col,round

# Read the data

df_campaign = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_socialmedia")



# Calculate multiple metrics at once
df_campaign = df_campaign \
    .withColumn("conversion_rate", round((col("conversions") / col("clicks")) * 100, 2)) \
    .withColumn("CTR", round((col("clicks") / col("impressions")) * 100, 2)) \
    .withColumn("CPC", round(col("social_media_cost") / col("clicks"), 2)) \
    .withColumn("CPA", round(col("social_media_cost") / col("conversions"), 2)) \
    .withColumn("ROAS", round(col("revenue") / col("social_media_cost"), 2)) \
    .withColumn("ROI", round((col("revenue") - col("social_media_cost")) / col("social_media_cost") * 100, 2)) \
    .withColumn("CES", round((col("conversion_rate") * 0.4) + (col("ctr") * 0.3) + (col("roas") * 0.3), 2))


df_campaign.show()
#To create dim_social_campaign table

df_campaign.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Social_Campaign")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
