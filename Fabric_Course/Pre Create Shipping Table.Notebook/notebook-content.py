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
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType

# Define the Delta table path
lakehouse_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_shipping"

# Check if the table exists
if not DeltaTable.isDeltaTable(spark, lakehouse_table_path):
    print("Table doesn't exist, creating it using Delta format.")

    # Define schema
    schema = StructType([
        StructField("ShippingID", IntegerType(), True),
        StructField("ProductID", IntegerType(), True),
        StructField("StoreID", IntegerType(), True),
        StructField("QuantityShipped", IntegerType(), True),
        StructField("ShippingDate", TimestampType(), True)
    ])

    # Create an empty DataFrame with schema
    empty_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)

    # Write as Delta table
    empty_df.write.format("delta").mode("overwrite").save(lakehouse_table_path)

    print("Empty Shipping table created successfully.")

else:

    print("Table already exists")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
