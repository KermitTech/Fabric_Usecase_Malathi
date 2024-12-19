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
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/Campaign/raw_customerprofiles"
)
df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# Function to mask the phone number: keeping the first and last digits and masking the rest
def mask_phone_number(phone):
    return F.when(
        F.col(phone).isNotNull(),
        F.concat(
            F.col(phone).substr(1, 1),  # Keep the first digit
            F.lit("****"),              # Mask in between
            F.col(phone).substr(-4, 4)  # Keep the last 4 digits
        )
    ).otherwise(F.lit("Masked Number"))

# Perform cleansing on the dataframe
df_cleaned = df.withColumn(
    "email",
    F.when(F.col("email").isNotNull(), F.concat(F.col("email").substr(1, 1), F.lit("***********@").substr(1, 11), F.col("email").substr(-4, 4))).otherwise(F.lit("masked@domain.com"))
).withColumn(
    "dob",
    F.when(F.col("dob").isNotNull(), F.lit("****-**-**")).otherwise(F.lit("****-**-**"))
).withColumn(
    "social_security_number",
    F.when(F.col("social_security_number").isNotNull(), F.concat(F.col("social_security_number").substr(1, 1), F.lit("********"), F.col("social_security_number").substr(-1, 1))).otherwise(F.lit("*********"))
).withColumn(
    "phone_number",
    mask_phone_number("phone_number")  # Apply the masking function to phone_number column
).dropna(subset=["customer_id", "first_name", "last_name"])

# Show cleaned data
df_cleaned.show()

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customerprofiles"  # Example of a table name

# Save the DataFrame as a Delta table
df_cleaned.write.format("delta").mode("overwrite").save(table_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Load cleansed Silver Layer tables

df_cust = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Campaign/cleansed_customerprofiles")

df_cust.show()

df_cust = df_cust.withColumn(
    "full_name", 
    F.concat(F.col("first_name"), F.lit(" "), F.col("last_name"))
)

# Drop the first_name and last_name columns
df_cust = df_cust.drop("first_name", "last_name")

#To create dim_customer table

df_cust.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer_campaign/Dim_Customer")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
