# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

source_path = "abfss://IMD_FAB_BIDM_ZAA_1003@onelake.dfs.fabric.microsoft.com/IMDBIDM_ZAA_Analytics_test.lakehouse/Tables/bronze/Account"
df = spark.read.format("delta").load(source_path)
print(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.read.format("delta").load(source_path)
print(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
