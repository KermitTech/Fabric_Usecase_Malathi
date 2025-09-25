# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c",
# META       "default_lakehouse_name": "Core42",
# META       "default_lakehouse_workspace_id": "0954d773-1b76-4837-90bb-56305401112a",
# META       "known_lakehouses": [
# META         {
# META           "id": "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

spark.sql("""
    DELETE FROM Core42.PipelineRunLog
    WHERE PreviousRunTime LIKE '%Z'
       OR CurrentRunTime LIKE '%Z'
""")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
