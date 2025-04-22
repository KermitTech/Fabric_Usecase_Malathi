# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************


import com.microsoft.spark.fabric
from com.microsoft.spark.fabric.Constants import Constants
df_source = spark.read.synapsesql("Silver.Supply_Chain.Cleansed_sales")
df_source_WH = spark.read.synapsesql("Gold.dbo.Dim_Date")
df_source.show()
df_source_WH.show()
#df_source.write.synapsesql("Gold.dbo.Dim_Date_test")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_source.show()
#df_source.write.synapsesql("Gold.dbo.Dim_Date_test")
df_source.write.mode("append").synapsesql("Gold.dbo.Dim_Date")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import com.microsoft.spark.fabric
from com.microsoft.spark.fabric.Constants import Constants
df = spark.read.synapsesql("Gold.dbo.Dim_Date")
df.show()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
