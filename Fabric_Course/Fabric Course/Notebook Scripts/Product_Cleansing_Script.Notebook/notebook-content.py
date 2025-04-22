# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql.functions import col, regexp_replace, udf, initcap
from pyspark.sql.types import FloatType, StringType
from pyspark.sql.types import BooleanType
from pyspark.sql import functions as F
import requests
from pyspark.sql.functions import col, when, lit, round
import json


# Read data from Lakehouse table
product_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_product"
)

# Before cleansing
product_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lower, trim, regexp_replace, lit


# Show initial data
print("Initial Data:")
product_df.show(truncate=False)

# Filter out the product id which is not null
product_df=product_df.filter(col("product_id").isNotNull())

# Filter out the product category which is not null
product_df=product_df.filter(col("category").isNotNull())

# 1. **Standardize Product Categories**: Normalize categories to lowercase
product_df = product_df.withColumn("category", lower(trim(col("category"))))

# Convert `is_discontinued` to Boolean
product_df = product_df.withColumn(
    "is_discontinued",
    when(col("is_discontinued").isin("True", "true", "1", "yes"), lit(True))
    .otherwise(lit(False))
)

# 2. **Remove Discontinued Products**: Filter out rows where `is_discontinued` is true
product_df = product_df.filter(~col("is_discontinued"))


# 4. **Normalize Product Names**:
# Remove special characters, trim whitespace, and standardize capitalization
product_df = product_df.withColumn(
    "product_name",
    regexp_replace(trim(col("product_name")), r"[^a-zA-Z0-9\s]", "")  # Remove special characters
)

# 5. **Classify and Handle SKUs**:
# Add a column to classify SKUs as missing, invalid, or valid
product_df = product_df.withColumn(
    "sku_status",
    when(col("sku").isNull(), lit("SKU_NOT_SPECIFIED"))  # If SKU is null
    .when(~col("sku").rlike(r"^[a-zA-Z0-9]{6,10}$"), lit("INVALID_SKU"))  # Invalid SKU pattern
    .otherwise(lit("VALID_SKU"))  # Otherwise valid
)

# Replace invalid or missing SKUs with placeholders if necessary (optional)
product_df = product_df.withColumn(
    "sku",
    when(col("sku_status") == "SKU_NOT_SPECIFIED", lit("NO_SKU_AVAILABLE"))
    .when(col("sku_status") == "INVALID_SKU", col("sku"))
    .otherwise(col("sku"))
)

# 6. **Final Cleansing**: Drop discontinued-related columns
product_df = product_df.drop("is_discontinued")

# Show results after all cleansing steps
print("Cleansed Data:")
product_df.show(truncate=False)


# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_product"  # Example of a table name

# Save the DataFrame as a Delta table
product_df.write.format("delta").mode("overwrite").save(table_name)



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
