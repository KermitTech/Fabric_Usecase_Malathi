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

# Create Spark session 
spark = SparkSession.builder.getOrCreate()

# Define the Fabric Lakehouse Path
new_parquet_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Files/Shipping/shipping_data.parquet"

# Read the Parquet file (New data)
new_shipping_df = spark.read.parquet(new_parquet_path)

# Show the New Data
print(" New Data from Parquet:")
new_shipping_df.show(5)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Define the Fabric Lakehouse Table
old_shipping_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_shipping"
)
# Load the Existing (Old) Lakehouse Table
#old_shipping_df = spark.read.format("delta").table(old_lakehouse_table)

# Show the Old Data
print(" Existing Data in Lakehouse Table:")
old_shipping_df.show(5)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql.functions import col

# Load the existing Delta table reference
deltaTable = DeltaTable.forPath(spark, f"abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_shipping")

# Merge condition (Matching on 'order_id')
deltaTable.alias("old").merge(
    new_shipping_df.alias("new"),
    "old.ShippingID = new.ShippingID"
).whenMatchedUpdate(set={
    "status": col("new.status"),
    "delivery_date": col("new.delivery_date")
}).whenNotMatchedInsert(values={
    "ShippingID": col("new.ShippingID"),
    "ProductID": col("new.ProductID"),
    "StoreID": col("new.StoreID"),
    "QuantityShipped": col("new.QuantityShipped"),
    "ShippingDate": col("new.ShippingDate")
}).execute()

print(" Merge (Upsert) Completed!")




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Reload the updated Lakehouse table
old_shipping_df_updated = spark.read.format("delta").table(old_lakehouse_table)

print(" Updated Lakehouse Table After Merge:")
old_shipping_df_updated.show(5)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
