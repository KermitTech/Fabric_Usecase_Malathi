# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

get_batch_id = 1

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable
from datetime import datetime
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.functions import col, current_timestamp, lit, when

opp_temp_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Opportunities"
tmp_control_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"
opp_raw_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Opportunities"


batch_id = get_batch_id

#  Load the raw table
opp_raw_df = spark.read.format("delta").load(opp_raw_path)

# Read the temporary table
opp_tmp_df = spark.read.format("delta").load(opp_temp_path)


# Add the Batch_id and Load_Type columns to the temp DataFrame
opp_tmp_df = opp_tmp_df \
    .withColumn("Batch_id", lit(batch_id)) \
    .withColumn("Load_Type", lit(None).cast("string"))  # Default to None (null)



# Step 2: Rename conflicting columns in the raw data to avoid duplicates
opp_raw_df_renamed = opp_raw_df.select(
    [col(c).alias(f"raw_{c}") if c != "id" else col(c) for c in opp_raw_df.columns]
)

opp_raw_df_renamed.show()

# Step 3: Perform a left join to identify existing records
opp_tmp = opp_tmp_df.join(
    opp_raw_df_renamed, 
    opp_tmp_df["Account_Name"] == opp_raw_df_renamed["raw_Account_Name"],  
    "left_outer"  # Keep all records from temp table
)



# Step 4: Set the Load_Type column based on whether the record exists
opp_tmp = opp_tmp.withColumn(
    "Load_Type",
    when(opp_tmp["raw_Account_Name"].isNotNull(), "Update")  # If it exists, it's an Update
    .otherwise("Insert")  # If it does not exist, it's an Insert
)



# Step 5: Drop the extra columns that were renamed
opp_tmp = opp_tmp.drop(*[col for col in opp_tmp.columns if col.startswith("raw_")])


# Overwrite the Tmp_Contact table with the updated schema
opp_tmp.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("overwrite") \
    .save(opp_temp_path)


# Calculate the max CreateDate
tmp_max_createdate = opp_tmp.agg({"CreatedDate": "max"}).collect()[0][0]
tmp_max_batchid = opp_tmp.agg({"Batch_id": "max"}).collect()[0][0]

max_value_timestamp = datetime.strptime('1990-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')

print(max_value_timestamp)

    # Define schema for the control entry
control_schema = StructType([
        StructField("TableName", StringType(), True),
        StructField("MaxValue", TimestampType(), True),
        StructField("Batch_id", StringType(), True),
        StructField("LastUpdated", TimestampType(), True),
        StructField("LastUpdatedBy", StringType(), True),
])



# If there is a max value (i.e., some data exists in the temporary table)
if tmp_max_createdate:
    # Create the control entry with the max created date
    tmp_control_entry = [{
            "TableName": "Tmp_Opportunities",
            "MaxValue": tmp_max_createdate,
            "Batch_id": tmp_max_batchid,  # Ensure batch_id is passed earlier
            "LastUpdated": None,  # Will be replaced by current_timestamp
            "LastUpdatedBy": ""  # Adjust based on your logic
    }]
    
else:
    # If there is no max value (empty table), set MaxValue as null
    tmp_control_entry = [{
            "TableName": "Tmp_Opportunities",
            "MaxValue": max_value_timestamp,
            "Batch_id": 0,  # Ensure batch_id is passed earlier
            "LastUpdated": None,  # Will be replaced by current_timestamp
            "LastUpdatedBy": ""  # Adjust based on your logic
    }]



# Convert the new control entry into a DataFrame
tmp_control_df = spark.createDataFrame(tmp_control_entry, schema=control_schema) \
        .withColumn("LastUpdated", current_timestamp())

# Read the existing control table
tmp_control_table = DeltaTable.forPath(spark, tmp_control_path)

# Merge into the control table: If entry exists, update; otherwise insert a new entry
tmp_control_table.alias("tmp_target").merge(
    tmp_control_df.alias("tmp_source"),
    "tmp_target.TableName = tmp_source.TableName"
).whenMatchedUpdate(
    set={
        "tmp_target.MaxValue": col("tmp_source.MaxValue"),
        "tmp_target.BatchValue": col("tmp_source.Batch_id"),
        "tmp_target.LastUpdated": col("tmp_source.LastUpdated"),
        "tmp_target.LastUpdatedBy": col("tmp_source.LastUpdatedBy")
    }
).whenNotMatchedInsert(
    values={
        "tmp_target.TableName": col("tmp_source.TableName"),
        "tmp_target.MaxValue": col("tmp_source.MaxValue"),
        "tmp_target.BatchValue": col("tmp_source.Batch_id"),
        "tmp_target.LastUpdated": col("tmp_source.LastUpdated"),
        "tmp_target.LastUpdatedBy": col("tmp_source.LastUpdatedBy")
    }
).execute()

# Print confirmation
if tmp_max_createdate:
    print(f"Opp table updated with MaxValue: {tmp_max_createdate} for Tmp_Opportunities.")
else:
    print("Opp table updated with null MaxValue for Tmp_Opportunities as no data was found.")


#organization_temp.show()

print(f"Tmp_Opportunities table updated with additional columns: Batch_id and Load_Type.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
