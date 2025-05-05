# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "ec021051-eec5-4ae4-a8c4-792ac985d6e1",
# META       "default_lakehouse_name": "Bronze_Layer",
# META       "default_lakehouse_workspace_id": "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"
# META     }
# META   }
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Initialize Spark session
spark = SparkSession.builder.appName("LakehouseTable").getOrCreate()

# Define the table path
table_path = 'abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Tables/dbo/raw_sales'

# Define the table schema
schema = StructType([
    StructField("transaction_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("product_id", StringType(), True),
    StructField("store_id", StringType(), True),
    StructField("sale_date", TimestampType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DecimalType(10, 2), True),
    StructField("discount", DecimalType(10, 2), True),
    StructField("sales_amount", DecimalType(10, 2), True)
])

# Check if the Delta table already exists at the specified location
if not DeltaTable.isDeltaTable(spark, table_path):
    # If the table doesn't exist, create it
    print("Table doesn't exist, creating table.")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS dbo.raw_sales (
            transaction_id INT,
            product_id STRING,
            store_id STRING,
            sale_date TIMESTAMP,
            quantity INT,
            unit_price DECIMAL(10, 2),
            discount DECIMAL(10, 2),
            sales_amount DECIMAL(10, 2)
        )
        USING DELTA
        LOCATION '{table_path}'
    """)
else:
    print("Table already exists.")

# If you want to overwrite the data (in case of existing data and new batch load), you can use:
# Example of overwriting the data:
# data_to_insert.write.format("delta").mode("overwrite").save(table_path)

# If you want to append data:
# data_to_insert.write.format("delta").mode("append").save(table_path)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
