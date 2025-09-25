# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql import SparkSession

# Create a Spark session (Databricks usually already has one running)
spark = SparkSession.builder.appName("LakehouseQuery").getOrCreate()

# Set the table name (replace with your own)
table_name = "abfss://Kermit_Tech_Core42@onelake.dfs.fabric.microsoft.com/Core42.Lakehouse/Tables/Opportunity_new"

#data_df = spark.read.format("delta").load(table_name)

# Pick the columns you want
columns = ["AccountId", "Name", "Account_Name_Alias__c", "Offerings__c", "Engagement_Model__c", "TCV_USD__c", "ABR_USD__c", "Sales_Stage__c"]


# Load the DataFrame (select only needed columns)
#df = spark.table(data_df).select(*columns)


# Load Delta table from ABFS path
data_df = spark.read.format("delta").load(table_name).select(*columns)

# Show top rows
data_df.show()




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
