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
from pyspark.sql.functions import col, current_timestamp, lit, when

org_temp_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Organisation"

# Read the temporary table
organization_tmp_df = spark.read.format("delta").load(org_temp_path)

# Add the Batch_id and Load_Type columns to the temp DataFrame
organization_temp = organization_tmp_df \
    .withColumn("Batch_id", lit(None).cast("int")) \
    .withColumn("Load_Type", lit(None).cast("string"))  # Default to None (null)

# Overwrite the Tmp_Organisation table with the updated schema
organization_temp.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("overwrite") \
    .save(org_temp_path)


organization_temp.show()

print(f"Tmp_Organisation table updated with additional columns: Batch_id and Load_Type.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
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

batch_id = 1 #get_batch_id

# Read the temporary table
organization_temp_df = spark.read.format("delta").load(organization_temp_path)

organization_temp_df.show()


# Merge into the destination Delta table
organization_table = DeltaTable.forPath(spark, organization_table_path)

print(organization_table)

# Perform the merge and capture the inserted rows count
merge_result = organization_table.alias("target").merge(
    organization_temp_df.alias("source"),
    "target.Account_Name = source.Account_Name"
).whenMatchedUpdate(set={
    "target.Phone": col("source.Phone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.CreatedDate": "source.CreatedDate",
    "target.Load_Type": lit("Update"),
    "target.UpdatedDate": current_timestamp(),
    "target.Batch_id": lit(batch_id)
}).whenNotMatchedInsert(values={
    "target.Account_Name": col("source.Account_Name"),
    "target.Phone": col("source.Phone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.CreatedDate": col("source.CreatedDate"),
    "target.Load_Type": lit("Insert"),
    "target.Batch_id": lit(batch_id)
}).execute()


inserted_rows_df = organization_temp_df.alias("source").join(
    organization_table.toDF().alias("target"), 
    col("source.Account_Name") == col("target.Account_Name"), 
    "inner"  # This will give us the rows that are now present in the target table
).filter((col("target.Batch_id") == lit(batch_id))  & (col("target.Load_Type") == lit("Insert"))) # Only select rows that were inserted in source

inserted_rows_count = inserted_rows_df.count()

print("Total records inserted:", inserted_rows_count)


if inserted_rows_count > 0:
    # Calculate the max created date from the inserted rows
    max_created_date = organization_table.toDF().agg({"CreatedDate": "max"}).collect()[0][0]
    

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
            "TableName": "Organisation",
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

from pyspark.sql.functions import col, current_timestamp, lit, when
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from delta.tables import DeltaTable

raw_org_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Organisation"
stg_org_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Salesforce_CRM/staging_organisation"
stg_control_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"

if DeltaTable.isDeltaTable(spark, stg_org_path):
    print(f"Delta table exists ")
else:
    print(f"No Delta table found ")

raw_organisation_df = spark.read.format("delta").load(raw_org_path)

print(raw_organisation_df)

# Merge into the destination Delta table
stg_organization_table = DeltaTable.forPath(spark, stg_org_path)

# Perform the merge and capture the inserted rows count
merge_result = stg_organization_table.alias("stg_target").merge(
    raw_organisation_df.alias("stg_source"),
    "stg_target.Account_Name = stg_source.Account_Name"
).whenMatchedUpdate(set={
    "stg_target.Phone": col("stg_source.Phone"),
    "stg_target.Account_Owner_Name": col("stg_source.Account_Owner_Name"),
    "stg_target.CreatedDate": col("stg_source.CreatedDate"),
    "stg_target.UpdatedDate": current_timestamp(),
    "stg_target.Load_Type": lit("Update"),
    "stg_target.Batch_id": col("stg_source.Batch_id")
}).whenNotMatchedInsert(values={
    "stg_target.Account_Name": col("stg_source.Account_Name"),
    "stg_target.Phone": col("stg_source.Phone"),
    "stg_target.Account_Owner_Name": col("stg_source.Account_Owner_Name"),
    "stg_target.CreatedDate": col("stg_source.CreatedDate"),
    "stg_target.Load_Type": lit("Insert"),
    "stg_target.Batch_id": col("stg_source.Batch_id")
}).execute()

stg_inserted_rows_df = raw_organisation_df.alias("stg_source").join(
    stg_organization_table.toDF().alias("stg_target"), 
    col("stg_source.Account_Name") == col("stg_target.Account_Name"), 
    "inner"  # This will give us the rows that are now present in the target table
).filter((col("stg_source.Batch_id") == col("stg_target.Batch_id")) & (col("stg_target.Load_Type") == lit("Insert")))  # Only select rows that were inserted in source

#stg_inserted_rows_df.show()

stg_inserted_rows_count = stg_inserted_rows_df.count()

print("Total records inserted:", stg_inserted_rows_count)

if stg_inserted_rows_count > 0:
    # Calculate the max created date from the inserted rows
    stg_max_created_date = organization_table.toDF().agg({"CreatedDate": "max"}).collect()[0][0]
    stg_max_batchid = organization_table.toDF().agg({"Batch_id": "max"}).collect()[0][0]

    # Explicitly define the schema for the control entry
    control_stg_schema = StructType([
        StructField("TableName", StringType(), True),
        StructField("MaxValue", TimestampType(), True),
        StructField("Batch_id", StringType(), True),
        StructField("LastUpdated", TimestampType(), True),
        StructField("LastUpdatedBy", StringType(), True),
    ])

    # Prepare the new control entry with correct schema
    stg_control_entry = [
        {
            "TableName": "Stg_Organisation",
            "MaxValue": stg_max_created_date,
            "Batch_id": stg_max_batchid,  # Ensure batch_id is passed earlier
            "LastUpdated": None,  # Will be replaced by current_timestamp
            "LastUpdatedBy": ""  # Adjust based on your logic
        }
    ]

    # Convert the new control entry to a DataFrame
    stg_control_entry_df = spark.createDataFrame(stg_control_entry, schema=control_stg_schema) \
        .withColumn("LastUpdated", current_timestamp())


    
    # Check if the control table already exists
    stg_control_table = DeltaTable.forPath(spark, stg_control_path)
    
    # Merge into the control table
    stg_control_table.alias("target_control").merge(
        stg_control_entry_df.alias("source_control"),
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

    print(f"Control table updated for 'Organization' with MaxValue: {stg_max_created_date}.")
else:
    print("No new inserts in Organization. Control table not updated.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
