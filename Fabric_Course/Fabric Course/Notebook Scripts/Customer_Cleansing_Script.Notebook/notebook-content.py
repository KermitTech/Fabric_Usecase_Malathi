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

df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_customer"
)
df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.functions import col, length, regexp_replace

# Remove rows with null or empty essential fields
df_cleaned = df.filter(
    (col("customer_id").isNotNull()) & (col("customer_name").isNotNull()) & (col("email").isNotNull())
)

# Validate email format (basic check)
df_cleaned = df_cleaned.filter(F.col("email").rlike("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))


# Validate phone number: Allow only digits, "+", "-", and spaces
df_cleaned = df_cleaned.withColumn("phone", regexp_replace(col("phone"), "[^0-9+\\- ]", ""))



# Ensure SSN (Social Security Number) has exactly 9 digits
df_cleaned = df_cleaned.filter(length(col("social_security_number")) >= 9)



# Ensure age is a valid number (between 0 and 120)
df_cleaned = df_cleaned.filter((col("age") >= 0) & (col("age") <= 120))

# Drop duplicate customer records based on customer_id
df_cleaned = df_cleaned.dropDuplicates(["customer_id"])

# Show cleaned data
df_cleaned.show()

# Define output table path for Fabric Lakehouse
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_customer"

# Save the DataFrame as a Delta table
df_cleaned.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
