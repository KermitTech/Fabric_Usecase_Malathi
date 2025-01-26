# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# PARAMETERS CELL ********************

get_batch_id = 0

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, current_timestamp, lit, when
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from delta.tables import DeltaTable

# Define paths
organization_temp_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Organisation"
organization_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Organisation"
control_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"

batch_id = get_batch_id

# Read the temporary table
organization_temp_df = spark.read.format("delta").load(organization_temp_path)



# Add Batch_id and Load_Type columns to the temp DataFrame
organization_temp_df = organization_temp_df \
    .withColumn("Batch_id", lit(batch_id)) \
    .withColumn("Load_Type", lit(None))  # Initialize Load_Type with None; it will be set during merge


# Merge into the destination Delta table
organization_table = DeltaTable.forPath(spark, organization_table_path)

# Perform the merge and capture the inserted rows count
merge_result = organization_table.alias("target").merge(
    organization_temp_df.alias("source"),
    "target.Account_Name = source.Account_Name"
).whenMatchedUpdate(set={
    "target.Phone": col("source.Phone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.UpdatedDate": current_timestamp(),
    "target.Load_Type": lit("UPDATE"),
    "target.Batch_id": lit(batch_id)
}).whenNotMatchedInsert(values={
    "target.Account_Name": col("source.Account_Name"),
    "target.Phone": col("source.Phone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.CreatedDate": current_timestamp(),
    "target.Load_Type": lit("INSERT"),
    "target.Batch_id": lit(batch_id)
}).execute()


inserted_rows_df = organization_temp_df.alias("source").join(
    organization_table.toDF().alias("target"), 
    col("source.Account_Name") == col("target.Account_Name"), 
    "inner"  # This will give us the rows that are now present in the target table
).filter(col("source.Batch_id") == batch_id)  # Only select rows that were inserted in source

inserted_rows_count = inserted_rows_df.count()

print("Total records inserted:", inserted_rows_count)


if inserted_rows_count > 0:
    # Calculate the max created date from the inserted rows
    max_created_date = organization_temp_df.agg({"CreatedDate": "max"}).collect()[0][0]
    

    # Explicitly define the schema for the control entry
    control_entry_schema = StructType([
        StructField("TableName", StringType(), True),
        StructField("MaxValue", TimestampType(), True),
        StructField("Batch_id", StringType(), True),
        StructField("LastUpdated", TimestampType(), True),
        StructField("LastUpdatedBy", StringType(), True),
    ])

    # Prepare the new control entry with correct schema
    new_control_entry = [
        {
            "TableName": "Organization",
            "MaxValue": max_created_date,
            "Batch_id": batch_id,  # Ensure batch_id is passed earlier
            "LastUpdated": None,  # Will be replaced by current_timestamp
            "LastUpdatedBy": ""  # Adjust based on your logic
        }
    ]

    # Convert the new control entry to a DataFrame
    new_control_entry_df = spark.createDataFrame(new_control_entry, schema=control_entry_schema) \
        .withColumn("LastUpdated", current_timestamp())


    
    # Check if the control table already exists
    control_table = DeltaTable.forPath(spark, control_table_path)
    
    # Merge into the control table
    control_table.alias("target_control").merge(
        new_control_entry_df.alias("source_control"),
        "target_control.TableName = source_control.TableName"
    ).whenMatchedUpdate(set={
        "target_control.MaxValue": col("source_control.MaxValue"),
        "target_control.BatchValue": col("source_control.Batch_id"),
        "target_control.LastUpdated": col("source_control.LastUpdated")
    }).whenNotMatchedInsert(values={
        "target_control.TableName": col("source_control.TableName"),
        "target_control.BatchValue": col("source_control.Batch_id"),
        "target_control.MaxValue": col("source_control.MaxValue"),
        "target_control.LastUpdated": col("source_control.LastUpdated")
    }).execute()

    print(f"Control table updated for 'Organization' with MaxValue: {max_created_date}.")
else:
    print("No new inserts in Organization. Control table not updated.")




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable

test_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Organisation"

if DeltaTable.isDeltaTable(spark, test_path):
    print(f"Delta table exists at: {test_path}")
else:
    print(f"No Delta table found at: {test_path}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
