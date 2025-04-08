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
from pyspark.sql.functions import col, sum

spark = SparkSession.builder.appName("DataQualityChecks").getOrCreate()



shipping_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_shipping")
inventory_df = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_inventory")

inventory_df.show()
shipping_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Step 1: Remove Duplicates
inventory_df = inventory_df.dropDuplicates()
print(" Removed duplicates.")

# Step 2: Handle Missing Values (Fill Nulls with Default Values)
# - Assuming `quantity_in_stock` missing values are replaced with 0
# - If `inventory_date` is missing, fill with '1970-01-01' as a placeholder
inventory_df = inventory_df.fillna({
    "quantity_in_stock": 0,
    "inventory_date": "1970-01-01"
})
print(" Handled missing values.")

# Step 3: Remove Negative Quantities
inventory_df = inventory_df.filter(col("quantity_in_stock") >= 0)
print("Removed negative quantities.")

inventory_df.show()

# Define Lakehouse Delta Table Path
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_inventory"  

# Step 4: Save Cleaned Inventory Data to the Lakehouse as a Delta Table
inventory_df.write.format("delta").mode("overwrite").save(table_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Step 1: Remove Shipping Duplicates
shipping_df = shipping_df.dropDuplicates()
print(" Removed duplicates from shipping data.")

# Step 2: Handle Missing Values in Shipping Data
# - Assuming `quantity_shipped` missing values are replaced with 0
# - If `shipping_date` is missing, fill with '1970-01-01' as a placeholder
shipping_df = shipping_df.fillna({
    "quantity_shipped": 0,
    "shipping_date": "1970-01-01"
})
print(" Handled missing values in shipping data.")

# Step 3: Remove Negative Quantities in Shipping Data
shipping_df = shipping_df.filter(col("quantity_shipped") >= 0)
print("Removed negative quantities from shipping data.")

shipping_df.show()



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F


# Step 2: Perform the join on both product_id and store_id
shipping_inventory_join = shipping_df.alias("shipping").join(
    inventory_df.alias("inventory"),
    (F.col("shipping.product_id") == F.col("inventory.product_id")) &
    (F.col("shipping.store_id") == F.col("inventory.store_id")),  # Add store_id condition to match on both
    "inner"
)
# Show the results of the join
shipping_inventory_join.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************




print(" Performed join to identify shipping data with matching inventory.")

# You can filter or save the result if needed
shipping_inventory_join_filtered = shipping_inventory_join.filter(
    F.col("shipping.product_id").isNotNull()  # You can filter based on the aliased column
)

shipping_inventory_join_filtered.show()

# Step 2: Check for Shipping Quantities is not Exceeding Inventory Quantities
#shipping_inventory_check = shipping_df.join(inventory_df, join_condition, "inner") \
 #   .filter(shipping_df["quantity_shipped"] < inventory_df["quantity_in_stock"])

shipping_inventory_join_filtered.show()
print("Identified records where shipping quantities exceed inventory quantities.")

shipping_inventory_check_filtered = shipping_inventory_join_filtered.filter(
    col("quantity_shipped") >= 0  # Example condition, remove zero or negative shipping quantities
)


# Select specific columns and avoid duplicate columns
shipping_inventory_join_selected = shipping_inventory_check_filtered.select(
    F.col("shipping.product_id"),
    F.col("shipping.shipping_id"),
    F.col("shipping.quantity_shipped"),
    F.col("shipping.store_id"),
    F.col("shipping.shipping_date")
)


# Define Lakehouse Delta Table Path for Shipping Data
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_shipping" 

# Step 4: Save Cleaned Shipping Data to the Lakehouse as a Delta Table
shipping_inventory_join_selected.write.format("delta").mode("overwrite").save(table_name)
shipping_inventory_join_selected.show()

print(f"Cleaned shipping data saved to: {table_name}")



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
