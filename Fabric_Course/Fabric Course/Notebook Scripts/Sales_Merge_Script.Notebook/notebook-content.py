# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

pip install sqlalchemy mysql-connector-python 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from sqlalchemy import create_engine 

from pyspark.sql import SparkSession 

# Initialize Spark session 

spark = SparkSession.builder \ 

    .appName("MySQL Connection Example") \ 

    .getOrCreate() 

# MySQL connection details 

host = "34.51.141.170" 

user = "root" 

password = “xxxxxxx” 

database = "demo" 

# Create SQLAlchemy engine for MySQL 

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}") 

# SQL query to fetch data 

query = "SELECT * FROM sales” 

# Fetch data using SQLAlchemy engine into a Pandas DataFrame 

pandas_df = pd.read_sql(query, engine) 

# Convert the Pandas DataFrame to a PySpark DataFrame 

new_sales_spark_df = spark.createDataFrame(pandas_df) 

# Show the data 

new_sales_spark_df.show() 


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable 

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DateType 

 

# Define the Delta table path 

lakehouse_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_sales" 

 

# Check if the table exists 

if not DeltaTable.isDeltaTable(spark, lakehouse_table_path): 

print("Table doesn't exist, creating it using Delta format.") 

 

# Define schema 

 

schema = StructType([ 

    StructField("transaction_id", IntegerType(), True), 

    StructField("product_id", StringType(), True), 

    StructField("store_id", StringType(), True), 

    StructField("customer_id", IntegerType(), True), 

    StructField("sale_date", TimestampType(), True), 

    StructField("quantity", IntegerType(), True), 

    StructField("unit_price", DecimalType(10, 2), True), 

    StructField("discount", DecimalType(5, 2), True), 

    StructField("sales_amount", DecimalType(10, 2), True) 

]) 

 

 

# Create an empty DataFrame with schema 

empty_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema) 

 

# Write as Delta table 

empty_df.write.format("delta").mode("overwrite").save(lakehouse_table_path) 

 

print("Empty Sales table created successfully.") 

 

else: 

 

print("Table already exists") 

 


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable 

 

# Load the Delta table as DeltaTable 

delta_sales_table = DeltaTable.forPath(spark, "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_sales") 

 

# Perform the upsert (merge) 

delta_sales_table.alias("existing").merge( 

new_sales_spark_df.alias("new"), 
 
"existing.transaction_id = new.transaction_id" 
  

).whenMatchedUpdate( 

condition="existing.sale_date < new.sale_date", 
 
set={ 
    "product_id": "new.product_id", 
    "store_id": "new.store_id", 
    "customer_id": "new.customer_id", 
    "sale_date": "new.sale_date", 
    "quantity": "new.quantity", 
    "unit_price": "new.unit_price", 
    "discount": "new.discount", 
    "sales_amount": "new.sales_amount" 
} 
  

).whenNotMatchedInsert( 

values={ 
    "transaction_id": "new.transaction_id", 
    "product_id": "new.product_id", 
    "store_id": "new.store_id", 
    "customer_id": "new.customer_id", 
    "sale_date": "new.sale_date", 
    "quantity": "new.quantity", 
    "unit_price": "new.unit_price", 
    "discount": "new.discount", 
    "sales_amount": "new.sales_amount" 
} 
  

).execute() 

 

 

print("Merge completed successfully.") 

 

 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
