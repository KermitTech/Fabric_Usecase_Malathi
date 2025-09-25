# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

API_URL = "https://api.core42.ai/v1/embeddings"
API_KEY = "e5524292062e4466b76e4c2e81352280"  # If required

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_embedding_from_core42(text, model="text-embedding-3-large"):
    payload = {
        "input": text,
        "model": model
    }
    print("▶️ Payload:", json.dumps(payload))
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("✖️ Error Response:", response.text)
        return None

    data = response.json()
    embedding = data['data'][0]['embedding']
    return embedding


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, to_timestamp

# Read pipeline runtime logs (assumes a table like: pipeline_logs_table)
runtime_df = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"


# Load the table
runtime_logs_df = spark.read.format("delta").load(runtime_df)

runtime_logs_df.select("PreviousRunTime", "CurrentRunTime").show(truncate=False)

#runtime_logs_df = runtime_logs_df.withColumn("PreviousRunTime", to_timestamp(col("PreviousRunTime"))) \
                       #.withColumn("CurrentRunTime", to_timestamp(col("CurrentRunTime")))


runtime_logs_df = runtime_logs_df.withColumn(
    "PreviousRunTime_ts",
    to_timestamp("PreviousRunTime", "M/d/yyyy h:mm:ss a")
).withColumn(
    "CurrentRunTime_ts",
    to_timestamp("CurrentRunTime", "yyyy-MM-dd'T'HH:mm:ss.SSSSSSSX"))



# Step 3: Get the latest runtime entry
latest_runtime_row = runtime_logs_df.orderBy(col("CurrentRunTime_ts").desc()).limit(1).collect()[0]



previous_str = latest_runtime_row["PreviousRunTime_ts"].strftime("%Y-%m-%d %H:%M:%S")
current_str = latest_runtime_row["CurrentRunTime_ts"].strftime("%Y-%m-%d %H:%M:%S")

print(f"Date range: {previous_str} → {current_str}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import requests
import json


opp_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/Opportunity"


# Define log table path
#log_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"

# Load the table
df = spark.read.format("delta").load(opp_table_path)

#df.show()

# Define your function
def create_document(row):
    return (
        f"Pursuit_Reference_Code_Bid_ID__c: {row['Pursuit_Reference_Code_Bid_ID__c']} "
        f"TCV_USD__c: {row['TCV_USD__c']} "
        f"Engagement_Model__c: {row['Engagement_Model__c']} "
        f"StageName: {row['StageName']} "
        f"ABR_Value__c: {row['ABR_Value__c']} "
    )

# Filter the DataFrame for one Bid ID
bid_id_to_test = 5618
filtered_df = df.filter(df["Pursuit_Reference_Code_Bid_ID__c"] == bid_id_to_test)

# Collect that one row
rows = filtered_df.limit(1).collect()

# Preview a few rows and print the concatenated document
#rows = df.limit(5).collect()


for row in rows:
    row_dict = row.asDict()
    text = create_document(row_dict)
    embedding = get_embedding_from_core42(text)

    print("Text:", text)
    print("Embedding:", embedding[:5] if embedding else "Failed")
    print("=" * 80)




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

!pip install pymongo

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pymongo import MongoClient


# Use your actual Cosmos DB Mongo connection string here
client = MongoClient("mongodb+srv://cosmos:Kermit1234@core42.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")

db = client["core42db"]
collection = db["embedded_collection"]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pymongo import MongoClient


# Use your actual Cosmos DB Mongo connection string here
client = MongoClient("mongodb+srv://cosmos:Kermit1234@core42.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")

db = client["core42db"]
collection = db["training_data"]

def create_document(row):
    return (
        f"Pursuit_Reference_Code_Bid_ID__c: {row['Pursuit_Reference_Code_Bid_ID__c']} "
        f"TCV_USD__c: {row['TCV_USD__c']} "
        f"Engagement_Model__c: {row['Engagement_Model__c']} "
        f"StageName: {row['StageName']} "
        f"ABR_Value__c: {row['ABR_Value__c']} "
    )

#rows = df.limit(5).collect()

# Filter the DataFrame for one Bid ID
bid_id_to_test = 5618
filtered_df = df.filter(df["Pursuit_Reference_Code_Bid_ID__c"] == bid_id_to_test)

# Collect that one row
rows = filtered_df.limit(1).collect()

for row in rows:
    row_dict = row.asDict()
    text = create_document(row_dict)
    embedding = get_embedding_from_core42(text)

    if not embedding:
        print("❌ Failed to get embedding. Skipping.")
        continue

    # Use the bid ID as a unique identifier (_id)
    record_id = str(row_dict.get("Pursuit_Reference_Code_Bid_ID__c"))

    # Optional: store only a few fields in metadata
    metadata = {
        "Sales_Stage__c": row_dict.get("Sales_Stage__c"),
        "TCV_USD__c": row_dict.get("TCV_USD__c"),
        "Engagement_Model__c": row_dict.get("Engagement_Model__c"),
        "StageName": row_dict.get("StageName"),
        "ABR_Value__c": row_dict.get("ABR_Value__c")
    }

    doc = {
        "_id": record_id,
        "embedding": embedding,
        "text": text,
        "metadata": metadata
    }

    # Upsert the document into Cosmos DB
    collection.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)

    print(f"✅ Upserted: {record_id}")
    print("=" * 80)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


from pyspark.sql.functions import to_timestamp, col, coalesce
from pymongo import MongoClient
import requests
import json

# Use your actual Cosmos DB Mongo connection string here
client = MongoClient("mongodb+srv://cosmos:Kermit1234@core42.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")

db = client["core42db"]
collection = db["embedded_collection"]


# --- Read and convert runtime logs ---
runtime_df = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/PipelineRunLog"
runtime_logs_df = spark.read.format("delta").load(runtime_df)

opp_table_path = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/Opportunity_test"


# Load the table
data_df = spark.read.format("delta").load(opp_table_path)




runtime_logs_df = runtime_logs_df.withColumn(
    "PreviousRunTime_ts",
    to_timestamp("PreviousRunTime", "M/d/yyyy h:mm:ss a")
).withColumn(
    "CurrentRunTime_ts",
    to_timestamp("CurrentRunTime", "yyyy-MM-dd'T'HH:mm:ss.SSSSSSSX")
)

latest_runtime = runtime_logs_df.orderBy(col("CurrentRunTime_ts").desc()).limit(1).collect()[0]

prev_runtime = latest_runtime["PreviousRunTime_ts"]
curr_runtime = latest_runtime["CurrentRunTime_ts"]

print(f"🕐 Date range: {prev_runtime} → {curr_runtime}")


# 1. Parse timestamp columns (adjust format if needed)
#data_df = data_df.withColumn(
 #   "LastModifiedDate_ts",
  #  to_timestamp("Last_ModifiedDate", "yyyy-MM-dd'T'HH:mm:ss.SSSSSSSX")
#).withColumn(
  #  "CreatedDate_ts",
  #  to_timestamp("CreatedDate", "yyyy-MM-dd'T'HH:mm:ss.SSSSSSSX")
#)

# 2. Fallback: use LastModifiedDate if present, else CreatedDate
data_df = data_df.withColumn(
    "EffectiveModified_ts",
    coalesce(col("Last_ModifiedDate"), col("CreatedDate"))
)

data_df.show()

# 3. Apply filter for incremental records
if prev_runtime is not None:
    print(f" Date range: {prev_runtime} → {curr_runtime}")
    filtered_df = data_df.filter(
        (col("EffectiveModified_ts") > prev_runtime) & (col("EffectiveModified_ts") <= curr_runtime)
    )
else:
    print(f" Initial load until: {curr_runtime}")
    filtered_df = data_df.filter(col("EffectiveModified_ts") <= curr_runtime)

filtered_df.show()

# --- Text Concatenation Function ---
def create_document(row):
    return (
        f"Pursuit_Reference_Code_Bid_ID__c: {row['Pursuit_Reference_Code_Bid_ID__c']} "
        f"TCV_USD__c: {row['TCV_USD__c']} "
        f"Engagement_Model__c: {row['Engagement_Model__c']} "
        f"StageName: {row['StageName']} "
        f"ABR_Value__c: {row['ABR_Value__c']} "
    )

# --- Process Rows and Upsert ---
rows = filtered_df.collect()
for row in rows:
    row_dict = row.asDict()
    text = create_document(row_dict)
    embedding = get_embedding_from_core42(text)

    if not embedding:
        print("❌ Failed to get embedding. Skipping.")
        continue

    record_id = str(row_dict.get("Pursuit_Reference_Code_Bid_ID__c"))
    metadata = {
        "Sales_Stage__c": row_dict.get("Sales_Stage__c"),
        "TCV_USD__c": row_dict.get("TCV_USD__c"),
        "Engagement_Model__c": row_dict.get("Engagement_Model__c"),
        "StageName": row_dict.get("StageName"),
        "ABR_Value__c": row_dict.get("ABR_Value__c")
    }

    doc = {
        "bid_id": record_id,
        "embedding": embedding,
        "text": text,
        "metadata": metadata
    }

    # Upsert the document into Cosmos DB
    collection.update_one({"bid_id": doc["bid_id"]}, {"$set": doc}, upsert=True)

    print(doc)

print(f"✅ Processed and upserted {len(rows)} records.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from bson import ObjectId
test_id = "3642"
#ObjectId("6863a8bd5678b363d7d4d3a4")  # or ObjectId("...") if needed
doc = collection.find_one({"bid_id": test_id})
print("Found doc:", doc)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import requests
import json


API_URL = "https://api.core42.ai/v1/embeddings"
API_KEY = "e5524292062e4466b76e4c2e81352280"  # If required

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_embedding_from_core42(text, model="text-embedding-3-large"):
    payload = {
        "input": text,
        "model": model
    }
    print("▶️ Payload:", json.dumps(payload))
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("✖️ Error Response:", response.text)
        return None

    data = response.json()
    embedding = data['data'][0]['embedding']
    return embedding

# Test it
sample_text = "hi"
emb = get_embedding_from_core42(sample_text)
print("Embedding vector (first 5 values):", emb[:5] if emb else "Failed")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
