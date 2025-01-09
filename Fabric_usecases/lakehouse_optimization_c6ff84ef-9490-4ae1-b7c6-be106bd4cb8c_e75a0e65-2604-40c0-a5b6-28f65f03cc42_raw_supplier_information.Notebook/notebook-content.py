# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "e75a0e65-2604-40c0-a5b6-28f65f03cc42",
# META       "default_lakehouse_name": "SupplyChain_Bronze_Layer",
# META       "default_lakehouse_workspace_id": "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c",
# META       "known_lakehouses": [
# META         {
# META           "id": "e75a0e65-2604-40c0-a5b6-28f65f03cc42",
# META           "name": "SupplyChain_Bronze_Layer"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Run the below script or schedule it to run regularly to optimize your Lakehouse table 'raw_supplier_information'

from delta.tables import *
deltaTable = DeltaTable.forName(spark, "raw_supplier_information")
deltaTable.optimize().executeCompaction()

# If you only want to optimize a subset of your data, you can specify an optional partition predicate. For example:
#
#     from datetime import datetime, timedelta
#     startDate = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
#     deltaTable.optimize().where("date > '{}'".format(startDate)).executeCompaction()

