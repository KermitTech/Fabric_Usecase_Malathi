# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "ec021051-eec5-4ae4-a8c4-792ac985d6e1",
# META       "default_lakehouse_name": "Bronze_Layer",
# META       "default_lakehouse_workspace_id": "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c",
# META       "known_lakehouses": [
# META         {
# META           "id": "ec021051-eec5-4ae4-a8c4-792ac985d6e1"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Step 1: Import necessary libraries
from pyspark.sql import SparkSession

# MySQL Connection Parameters
mysql_host = "35.235.241.240"
mysql_port = "3306"
mysql_database = "demo"
mysql_table = "product_catalog"
mysql_user = "root"
mysql_password = "StreamTra1ningSets!"  # Use Fabric secrets recommended

# Step 3: Create a JDBC connection URL
connection_string = f"jdbc:mysql://{mysql_host}:{mysql_port}/{mysql_database}?serverTimezone=UTC&useSSL=false"

# Step 4: Initialize Spark session and configure JDBC driver
spark = SparkSession.builder \
    .appName("MySQL-Connection") \
    .config("spark.jars.packages", "mysql:mysql-connector-java:8.0.29").getOrCreate()

# Step 5: Read data from MySQL using JDBC
mysql_df = spark.read \
    .format("jdbc") \
    .option("url", connection_string) \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", mysql_table) \
    .option("user", mysql_user) \
    .option("password", mysql_password) \
    .load()

# Step 6: Display the DataFrame (first 5 rows as a sample)
display(mysql_df)

# Step 7 (Optional): Save data to Lakehouse or Delta table in Fabric (Bronze Layer)
mysql_df.write.format("delta").mode("overwrite").saveAsTable("bronze_mysql_table")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
