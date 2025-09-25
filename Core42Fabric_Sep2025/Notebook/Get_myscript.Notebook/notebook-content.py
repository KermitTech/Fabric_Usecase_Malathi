# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

schema = "script_name STRING, code STRING"
df = spark.read.option("multiline", "true")\
    .schema(schema)\
    .json("abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Files/fabriccode/testjson.json")
#df.show(truncate=False)
row = df.collect()[0]
script_name = row["script_name"]
code_str = row["code"]

print(code_str)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

file_loc = ""
with open(f"{script_name}_test.py", "w") as f:
    f.write(code_str)

print(f"Saved as: {script_name}_test.py")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
