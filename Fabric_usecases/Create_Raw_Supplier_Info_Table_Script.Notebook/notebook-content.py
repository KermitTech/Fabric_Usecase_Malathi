# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Initialize Spark session
spark = SparkSession.builder.appName("LakehouseTable").getOrCreate()

# Define the table path
table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/SupplyChain_Bronze_Layer.Lakehouse/Tables/raw_supplier_info"



# Define the schema for the error table
schema = StructType([
    StructField("supplier_id", IntegerType(), False),        # Unique supplier identifier
    StructField("supplier_name", StringType(), True),        # Supplier's name
    StructField("company_name", StringType(), True),         # Supplier's company name
    StructField("contact_name", StringType(), True),         # Contact person for the supplier
    StructField("contact_title", StringType(), True),        # Contact's title
    StructField("phone_number", StringType(), True),         # Supplier's contact phone number
    StructField("email", StringType(), True),                # Supplier's email address
    StructField("address_line1", StringType(), True),        # Supplier's address line 1
    StructField("address_line2", StringType(), True),        # Supplier's address line 2
    StructField("city", StringType(), True),                 # Supplier's city
    StructField("state", StringType(), True),                # Supplier's state
    StructField("zip_code", StringType(), True),             # Supplier's ZIP/Postcode
    StructField("country", StringType(), True),              # Supplier's country
    StructField("tax_id", StringType(), True)                # Supplier's tax ID
])
# Create an empty DataFrame using the schema
empty_df = spark.createDataFrame([], schema)

# Create a table in the Lakehouse or any target database
# Replace 'database_name' with the desired database and 'error_table' with the table name
empty_df.write.format("delta").mode("overwrite").save(table_path)

print("Supplier table created successfully!")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
