-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   },
-- META   "dependencies": {}
-- META }

-- CELL ********************

# Step 1: Load data from Fabric Warehouse (assuming the table is called Contact)
df = spark.sql("""
SELECT 
    FirstName, 
    LastName, 
    Email, 
    CreatedDate
FROM 
    [salesforce_CRM].[Contact]
WHERE 
    CreatedDate > '2022-01-01'
""")

# Show the first few records to verify the data
df.show()

# Step 2: Perform some basic transformations on the DataFrame (for example, adding a new column)
df_transformed = df.withColumn("FullName", df["FirstName"] + " " + df["LastName"])

# Show the transformed data
df_transformed.show()

# Step 3: Write the transformed data back to a different table in Fabric Warehouse
df_transformed.write.format("delta").mode("overwrite").saveAsTable("[salesforce_CRM].[Contact_Transformed]")

# Step 4: Verify that the transformed data has been written back
df_check = spark.sql("""
SELECT * FROM [salesforce_CRM].[Contact_Transformed]
""")
df_check.show()


-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

from pyspark.sql import functions as F
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("DeltaTableTest").getOrCreate()

# Set ABFS path for the Delta table in Fabric Warehouse
abfs_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Salesforce_CRM.datawarehouse/Tables/salesforce_CRM/Testtable"

# Step 1: Read the existing Delta table (assuming it's already created in the Fabric warehouse)
df_existing = spark.read.format("delta").load(abfs_path)

# Step 2: Perform some simple transformations or modifications on the data
# Example: Update the "Email" column to lowercase and change the "Mobile" column to "1234567890"
df_updated = df_existing.withColumn("Email", F.lower(F.col("Email"))) \
                       .withColumn("Mobile", F.lit("1234567890"))

# Step 3: Overwrite the Delta table with the updated data
df_updated.write.format("delta").mode("overwrite").save(abfs_path)

# Step 4: Verify the update (Read back the data)
df_verified = spark.read.format("delta").load(abfs_path)
df_verified.show()

# Stop the Spark session after testing
spark.stop()


-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Initialize Spark session
spark = SparkSession.builder.appName("IncrementalLoad").getOrCreate()

# Set ABFS paths for your tables
destination_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Salesforce_CRM.datawarehouse/Tables/salesforce_CRM/Contact_Dest"
temp_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Salesforce_CRM.datawarehouse/Tables/salesforce_CRM/Contact_temp"

# Read the Delta tables
destination_df = spark.read.format("delta").load(destination_table_path)
temp_df = spark.read.format("delta").load(temp_table_path)

# Make sure that DeltaTable is initialized for merge
destination_table = DeltaTable.forPath(spark, destination_table_path)
#temp_table = DeltaTable.forPath(spark, temp_table_path)

# Perform the MERGE operation to update and insert data
destination_table.alias("dest").merge(
    temp_table.alias("temp"),
    "dest.Email = temp.Email"  # Specify the matching condition (you can use any column you prefer for matching)
).whenMatchedUpdate(
    condition="dest.CreatedDate < temp.CreatedDate",  # Only update if the temp record has a newer CreatedDate (or other logic)
    set={
        "FirstName": "temp.FirstName",
        "LastName": "temp.LastName",
        "Email": "temp.Email",
        "Phone": "temp.Phone",  # Example of columns to update
    }
).whenNotMatchedInsert(
    values={
        "FirstName": "temp.FirstName",
        "LastName": "temp.LastName",
        "Email": "temp.Email",
        "Phone": "temp.Phone",  # Example of columns to insert
        "CreatedDate": "temp.CreatedDate"
    }
).execute()

# After the merge, you can continue with additional transformations or operations if needed.

# Stop the Spark session after the operations
spark.stop()


-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- Assuming the destination table is `Contact` and the temp table is `Temp_Salesforce_Records`

-- Perform a merge (upsert) directly from the temp table into the destination table
MERGE INTO salesforce_CRM.Contact_temp AS target
USING salesforce_CRM.Contact_Dest AS source
ON target.Email = source.Email  -- Matching condition, could be any field
WHEN MATCHED AND target.CreatedDate < source.CreatedDate THEN
    UPDATE SET
        target.FirstName = source.FirstName,
        target.LastName = source.LastName,
        target.Email = source.Email,
        target.Phone = source.Phone,
        target.UpdatedDate = source.UpdatedDate
WHEN NOT MATCHED THEN
    INSERT (FirstName, LastName, Email, Phone, CreatedDate, UpdatedDate)
    VALUES (source.FirstName, source.LastName, source.Email, source.Phone, source.CreatedDate, source.UpdatedDate);


-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
