# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType

# Define a simple list of positive and negative words (can be expanded)
positive_words = ["good", "great", "very much", "liked", "excellent", "happy", "joy", "love", "positive", "best", "super", "amazing"]
negative_words = ["bad", "poor", "late", "delayed", "damaged", "out of stock", "worst", "less", "hate", "sad", "negative", "awful", "angry", "not like", "not available"]

# Define a function to calculate sentiment based on word counts, including multi-word phrases
def simple_sentiment_analysis(feedback_text):
    # Convert text to lowercase to ensure case-insensitivity
    feedback_text = feedback_text.lower()
    
    # Initialize counts for positive and negative words
    positive_count = sum(phrase in feedback_text for phrase in positive_words)
    negative_count = sum(phrase in feedback_text for phrase in negative_words)
    
    # Initialize counts for individual words (to handle single words)
    positive_word_count = sum(word in feedback_text.split() for word in positive_words if word not in positive_words)
    negative_word_count = sum(word in feedback_text.split() for word in negative_words if word not in negative_words)
    
    # Calculate sentiment score: positive, negative or neutral
    sentiment_score = 0.0  # Default to neutral
    
    # First, check for phrases and assign sentiment
    if positive_count > negative_count:
        sentiment_score = 1.0  # Positive sentiment
    elif negative_count > positive_count:
        sentiment_score = -1.0  # Negative sentiment
    elif positive_word_count > negative_word_count:
        sentiment_score = 1.0  # Positive sentiment
    elif negative_word_count > positive_word_count:
        sentiment_score = -1.0  # Negative sentiment

    return sentiment_score

# Register the UDF with Spark
sentiment_analysis_udf = udf(simple_sentiment_analysis, FloatType())



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Categorization UDF
def categorize_feedback(feedback_text: str) -> str:
    if feedback_text:
        feedback_text = feedback_text.lower()
        
        # Define categories based on keywords
        if "service" in feedback_text or "support" in feedback_text or "customer" in feedback_text:
            return "Customer Service"
        elif "product" in feedback_text or "quality" in feedback_text or "damaged" in feedback_text:
            return "Product Quality"
        elif "price" in feedback_text or "cost" in feedback_text:
            return "Pricing"
        elif "experience" in feedback_text or "user-friendly" in feedback_text:
            return "User Experience"
        elif "delivery" in feedback_text or "delayed" in feedback_text or "shipping" in feedback_text:
            return "Product Delivery"
        elif "discounts" in feedback_text:
            return "Product Discounts"
        elif "stocks" in feedback_text:
            return "Product Stocks"
        else:
            return "General"
    return "Unknown"

# Register the UDF
categorize_feedback_udf = udf(categorize_feedback, StringType())


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import re
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.functions import udf

# Define a UDF for key phrase extraction using regular expressions
def extract_key_phrases(feedback_text):
    # Preprocess the feedback text
    feedback_text = feedback_text.lower()  # Convert to lowercase for consistency
    
    # Define a pattern to extract key phrases (nouns, adjectives, and combinations)
    # Match phrases with nouns and adjectives; consider basic noun-adjective pairs
    #pattern = r'\b(?:[a-zA-Z]+(?: [a-zA-Z]+)*)\b'  # Extract words or combinations of words
    pattern = r'\b[a-zA-Z]+\b'
    key_phrases = re.findall(pattern, feedback_text)
    
    # Additional filters to remove common stop words (optional)
    stop_words = {'the', 'and', 'was', 'is', 'in', 'a', 'to', 'of', 'for', 'on'}
    key_phrases = [phrase for phrase in key_phrases if phrase not in stop_words]

    # Join the key phrases into a single string (or keep as a list)
    return ', '.join(key_phrases)

# Register the UDF with Spark
extract_key_phrases_udf = udf(extract_key_phrases, StringType())



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col, trim, regexp_replace, lit, length, current_date, row_number
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType

# Load the tables
campaign_survey_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_survey"
)
campaign_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign"
)
email_campaign_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_email_campaign"
)

# Load the existing error table from Lakehouse
error_table = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details")

# Get the current max error_id from the error table
current_max_error_id = error_table.agg(F.max("error_id").alias("max_error_id")).collect()[0]["max_error_id"]
if current_max_error_id is None:
    current_max_error_id = 0  # Start at 0 if the error table is empty

# Step 1: Validate Data
# - Remove rows with NULL or empty feedback_text
# - Ensure rating is between 1 and 5
invalid_feedback = campaign_survey_df.filter(
    (trim(col("feedback_text")) == "") | (col("feedback_text").isNull())
)

campaign_survey_df = campaign_survey_df.filter(
    (trim(col("feedback_text")) != "") | (col("feedback_text").isNotNull())
)
invalid_rating = campaign_survey_df.filter(
    (col("rating") < 1) | (col("rating") > 5)
)

campaign_survey_df = campaign_survey_df.filter(
    (col("rating") > 1) | (col("rating") < 5)
)

# Log validation errors for empty feedback (NULL or empty strings)
empty_feedback_error = invalid_feedback.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    col("campaign_id").alias("error_key"),
    lit("Feedback is empty or NULL.").alias("error_description"),
    F.current_timestamp().alias("created_date")
)

# Log validation errors for invalid rating (outside the 1-5 range)
invalid_rating_error = invalid_rating.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    col("campaign_id").alias("error_key"),
    lit("Rating is invalid. Must be between 1 and 5.").alias("error_description"),
    F.current_timestamp().alias("created_date")
)

# Combine the errors into the error table
error_table = error_table.unionByName(empty_feedback_error)
error_table = error_table.unionByName(invalid_rating_error)

# Additional Validations:

# 1. Validate missing campaign_id (Null or missing)
missing_campaign_id = campaign_survey_df.filter(col("campaign_id").isNull())
missing_campaign_id_error = missing_campaign_id.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    lit("NULL").alias("error_key"),
    lit("Missing campaign_id.").alias("error_description"),
    F.current_timestamp().alias("created_date")
)
error_table = error_table.unionByName(missing_campaign_id_error)

# 2. Validate feedback text length (too short)
short_feedback = campaign_survey_df.filter(
    (length(trim(col("feedback_text"))) < 4) & (col("feedback_text").isNotNull())
)
short_feedback_error = short_feedback.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    col("campaign_id").alias("error_key"),
    lit("Feedback text is too short (less than 4 characters).").alias("error_description"),
    F.current_timestamp().alias("created_date")
)
error_table = error_table.unionByName(short_feedback_error)


campaign_survey_df = campaign_survey_df.filter(
    (length(trim(col("feedback_text"))) > 4))

# 3. Validate missing feedback text
missing_feedback = campaign_survey_df.filter(col("feedback_text").isNull())
missing_feedback_error = missing_feedback.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    col("campaign_id").alias("error_key"),
    lit("Missing feedback text.").alias("error_description"),
    F.current_timestamp().alias("created_date")
)
error_table = error_table.unionByName(missing_feedback_error)





# Filter out rows with invalid feedback from the campaign_survey_df
campaign_survey_df = campaign_survey_df.withColumn(
    "feedback_text",
    regexp_replace(col("feedback_text"), "[^a-zA-Z0-9\\s]", "")
).filter(
    col("feedback_text").isNotNull() &
    (regexp_replace(col("feedback_text"), "[^a-zA-Z0-9\\s]", "") == col("feedback_text"))
)




# Step 4: Validate if campaign_id exists in the valid campaign list
valid_campaign_ids_df = campaign_df.select("campaign_id").union(email_campaign_df.select("campaign_id"))

# Filter out invalid campaign ids
invalid_campaign_ids = campaign_survey_df.join(valid_campaign_ids_df, on="campaign_id", how="left_anti")

# Log validation errors for invalid campaign_ids
invalid_campaign_ids_error = invalid_campaign_ids.withColumn(
    "error_id", row_number().over(Window.orderBy(lit(1))) + lit(current_max_error_id)
).select(
    col("error_id"),
    lit("campaign_survey").alias("entity_name"),
    col("campaign_id").alias("error_key"),
    lit("Invalid campaign_id. Not found in valid campaigns.").alias("error_description"),
    F.current_timestamp().alias("created_date")
)

# Append the invalid campaign_id errors to the error table
error_table = error_table.unionByName(invalid_campaign_ids_error)

# Step 5: Join to get valid survey data
cleansed_df = valid_campaign_ids_df.join(campaign_survey_df, ["campaign_id"], "inner")

# Step 6: Apply UDFs (as per your existing pipeline)
# Assume UDFs for sentiment, category, and key phrases are defined as per your existing code.
cleansed_df = cleansed_df.withColumn('sentiment_score', sentiment_analysis_udf('feedback_text'))
cleansed_df = cleansed_df.withColumn('category', categorize_feedback_udf('feedback_text'))
cleansed_df = cleansed_df.withColumn('key_phrases', extract_key_phrases_udf('feedback_text'))

# Show cleansed data
cleansed_df.show(truncate=False)
error_table.show(truncate=False)
# Step 7: Save Cleansed Data (valid data)
cleansed_df.write.format("delta").mode("overwrite").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_campaign_survey")

# Step 8: Save the error table (append mode)
error_table.write.format("delta").mode("append").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Error_log_details")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
