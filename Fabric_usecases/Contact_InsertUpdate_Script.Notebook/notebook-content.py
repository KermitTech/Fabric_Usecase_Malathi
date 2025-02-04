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

contact_temp_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Contact"
tmp_control_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"
contact_raw_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Contact"


batch_id = get_batch_id

#  Load the raw table
contact_raw_df = spark.read.format("delta").load(contact_raw_path)

# Read the temporary table
contact_tmp_df = spark.read.format("delta").load(contact_temp_path)


# Add the Batch_id and Load_Type columns to the temp DataFrame
contact_tmp_df = contact_tmp_df \
    .withColumn("Batch_id", lit(batch_id)) \
    .withColumn("Load_Type", lit(None).cast("string"))  # Default to None (null)



# Step 2: Rename conflicting columns in the raw data to avoid duplicates
contact_raw_df_renamed = contact_raw_df.select(
    [col(c).alias(f"raw_{c}") if c != "id" else col(c) for c in contact_raw_df.columns]
)

contact_raw_df_renamed.show()

# Step 3: Perform a left join to identify existing records
contact_tmp = contact_tmp_df.join(
    contact_raw_df_renamed, 
    contact_tmp_df["Account_Name"] == contact_raw_df_renamed["raw_Account_Name"],  
    "left_outer"  # Keep all records from temp table
)



# Step 4: Set the Load_Type column based on whether the record exists
contact_tmp = contact_tmp.withColumn(
    "Load_Type",
    when(contact_tmp["raw_Account_Name"].isNotNull(), "Update")  # If it exists, it's an Update
    .otherwise("Insert")  # If it does not exist, it's an Insert
)



# Step 5: Drop the extra columns that were renamed
contact_tmp = contact_tmp.drop(*[col for col in contact_tmp.columns if col.startswith("raw_")])


# Overwrite the Tmp_Contact table with the updated schema
contact_tmp.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("overwrite") \
    .save(contact_temp_path)


# Calculate the max CreateDate
tmp_max_createdate = contact_tmp.agg({"CreatedDate": "max"}).collect()[0][0]
tmp_max_batchid = contact_tmp.agg({"Batch_id": "max"}).collect()[0][0]

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
            "TableName": "Tmp_Contact",
            "MaxValue": tmp_max_createdate,
            "Batch_id": tmp_max_batchid,  # Ensure batch_id is passed earlier
            "LastUpdated": None,  # Will be replaced by current_timestamp
            "LastUpdatedBy": ""  # Adjust based on your logic
    }]
    
else:
    # If there is no max value (empty table), set MaxValue as null
    tmp_control_entry = [{
            "TableName": "Tmp_Contact",
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
    print(f"Control table updated with MaxValue: {tmp_max_createdate} for Tmp_Contact.")
else:
    print("Control table updated with null MaxValue for Tmp_Contact as no data was found.")


#organization_temp.show()

print(f"Tmp_Contact table updated with additional columns: Batch_id and Load_Type.")

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
contact_temp_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Contact"
contact_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Contact"
control_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"

batch_id = get_batch_id

# Read the temporary table
contact_temp_df = spark.read.format("delta").load(contact_temp_path)

contact_temp_df.show()


# Merge into the destination Delta table
contact_table = DeltaTable.forPath(spark, contact_table_path)


# Perform the merge and capture the inserted rows count
merge_result = contact_table.alias("target").merge(
    contact_temp_df.alias("source"),
    "target.Account_Name = source.Account_Name"
).whenMatchedUpdate(set={
    "target.Phone": col("source.Phone"),
    "target.Title": col("source.Title"),
    "target.MobilePhone": col("source.MobilePhone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.FirstName": col("source.FirstName"),
    "target.LastName": col("source.LastName"),
    "target.MailingCountry": col("source.MailingCountry"),
    "target.MailingState": col("source.MailingState"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.CreatedDate": "source.CreatedDate",
    "target.Load_Type": lit("Update"),
    "target.UpdatedDate": current_timestamp(),
    "target.Batch_id": lit(batch_id)
}).whenNotMatchedInsert(values={
    "target.Account_Name": col("source.Account_Name"),
    "target.Phone": col("source.Phone"),
    "target.Title": col("source.Title"),
    "target.MobilePhone": col("source.MobilePhone"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.FirstName": col("source.FirstName"),
    "target.LastName": col("source.LastName"),
    "target.MailingCountry": col("source.MailingCountry"),
    "target.MailingState": col("source.MailingState"),
    "target.Account_Owner_Name": col("source.Account_Owner_Name"),
    "target.CreatedDate": "source.CreatedDate",
    "target.Load_Type": lit("Insert"),
    "target.UpdatedDate": current_timestamp(),
    "target.Batch_id": lit(batch_id)
}).execute()


inserted_rows_df = contact_temp_df.alias("source").join(
    contact_table.toDF().alias("target"), 
    col("source.Account_Name") == col("target.Account_Name"), 
    "inner"  # This will give us the rows that are now present in the target table
).filter((col("target.Batch_id") == lit(batch_id))  & (col("target.Load_Type") == lit("Insert"))) # Only select rows that were inserted in source

inserted_rows_count = inserted_rows_df.count()

print("Total records inserted:", inserted_rows_count)


if inserted_rows_count > 0:
    # Calculate the max created date from the inserted rows
    max_created_date = contact_table.toDF().agg({"CreatedDate": "max"}).collect()[0][0]
    

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
            "TableName": "Contact",
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

    print(f"Control table updated for 'Contact' with MaxValue: {max_created_date}.")
else:
    print("No new inserts in Contact. Control table not updated.")




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
