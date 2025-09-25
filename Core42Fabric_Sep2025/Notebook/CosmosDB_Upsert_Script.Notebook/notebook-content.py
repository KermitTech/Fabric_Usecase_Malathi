# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
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
collection = db["training_data"]


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

doc = {
    "_id": "5618",
    "offerings": "Healthcare",
    "sub_offerings": "Healthcare"
}

# Use upsert=True for insert-or-update
collection.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from bson import ObjectId

filter_id =  5432
#ObjectId("6863a8bd5678b363d7d4d3a4")
doc_coll = collection.find_one({"bid_id": filter_id})
print("Found doc:", doc)

doc_coll = {
    "bid_id": filter_id,
    "_id": filter_id,
    "offerings": "TestValue05",
    "sub_offerings": "TestValue05",
    "account_name": "Louvre Abu Dhabi",
    "core42_vertical": "Healthcare",
    "engagement_model": "RFP",
    "tcv_usd": 1000,
    "abr_usd": 1000,
    "sales_stage": "Cancelled"
}

# Use upsert=True for insert-or-update
result = collection.update_one({"bid_id": doc_coll["bid_id"]}, {"$set": doc_coll}, upsert=True)
print(result.raw_result)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from bson import ObjectId
import json

test_id = ObjectId("6863a8bd5678b363d7d4d3a4")  # or ObjectId("...") if needed
doc = collection.find_one({"_id": test_id})
print("Found doc:", doc)

if doc:
    print(json.dumps(doc, indent=5, default=str))
else:
    print("No document found with _id =", id_value)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from bson import ObjectId
test_id = '5618'
#ObjectId("6863a8bd5678b363d7d4d3a4")  # or ObjectId("...") if needed
doc = collection.find_one({"_id": test_id})
print("Found doc:", doc)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from bson import ObjectId
test_id = 5432
#ObjectId("6863a8bd5678b363d7d4d3a4")  # or ObjectId("...") if needed
doc = collection.find_one({"bid_id": test_id})
print("Found doc:", doc)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

