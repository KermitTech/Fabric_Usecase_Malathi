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
from pyspark.sql.functions import year, month, dayofweek, col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator


spark = SparkSession.builder.appName("DemandForecasting").getOrCreate() 

# Read the sales_transactions.csv into a Spark DataFrame
sales_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_sales"
)
  

sales_df = sales_df.withColumn("Year", year("sale_date")) \
    .withColumn("Month", month("sale_date")) \
    .withColumn("DayOfWeek", dayofweek("sale_date")) 


sales_df.show()




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************



#Load Datasets 


inventory_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_inventory"
)

inventory_df.show()

shipping_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_shipping"
)
shipping_df.show()


 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import sum as spark_sum

# Aggregate sales data
sales_agg = sales_df.groupBy("product_id", "store_id", "sale_date") \
                    .agg(spark_sum("quantity").alias("TotalQuantitySold"))

sales_agg.show()

# Aggregate shipping data
shipping_agg = shipping_df.groupBy("product_id", "store_id", "shipping_date") \
                          .agg(spark_sum("quantity_shipped").alias("TotalQuantityShipped"))

shipping_agg.show()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import coalesce, lit

# Join sales and shipping data
combined_df = sales_agg.join(shipping_agg,
                             (sales_agg.product_id == shipping_agg.product_id) &
                             (sales_agg.store_id == shipping_agg.store_id) &
                             (sales_agg.sale_date == shipping_agg.shipping_date),
                             "outer") \
                       .select(coalesce(sales_agg.product_id, shipping_agg.product_id).alias("product_id"),
                               coalesce(sales_agg.store_id, shipping_agg.store_id).alias("store_id"),
                               coalesce(sales_agg.sale_date, shipping_agg.shipping_date).alias("Date"),
                               coalesce(sales_agg.TotalQuantitySold, lit(0)).alias("TotalQuantitySold"),
                               coalesce(shipping_agg.TotalQuantityShipped, lit(0)).alias("TotalQuantityShipped"))

# Join with inventory data to get initial stock levels
final_df = combined_df.join(inventory_df, ["product_id", "store_id"], "left") \
                      .select("product_id", "store_id", "Date", "TotalQuantitySold", "TotalQuantityShipped", "quantity_in_stock")

final_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.window import Window
from pyspark.sql.functions import sum as spark_sum, col

# Define window specification
window_spec = Window.partitionBy("product_id", "store_id").orderBy("Date") \
                    .rowsBetween(Window.unboundedPreceding, 0)

# Calculate cumulative stock level
final_df = final_df.withColumn("StockLevel",
                               col("quantity_in_stock") -
                               spark_sum("TotalQuantitySold").over(window_spec) +
                               spark_sum("TotalQuantityShipped").over(window_spec))

final_df = final_df.withColumn("Year", year("Date")) \
    .withColumn("Month", month("Date")) \
    .withColumn("DayOfWeek", dayofweek("Date")) 

final_data_filled = final_df.fillna(0, subset=["StockLevel", "quantity_in_stock", "TotalQuantitySold", "TotalQuantityShipped", "Year", "Month", "DayOfWeek"])

final_data_filled.show()

# Define Lakehouse Delta Table Path
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Demand_Forecasting_Sales_Analysis"  

# Step 4: Save Cleaned Inventory Data to the Lakehouse as a Delta Table
final_data_filled.write.format("delta").mode("overwrite").save(table_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import RegressionEvaluator


# Define feature columns
feature_columns = ["StockLevel", "quantity_in_stock","TotalQuantityShipped", "Year", "Month", "DayOfWeek"]

# Assemble features
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
data = assembler.transform(final_data_filled)




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

# Split data into training and test sets
train_data, test_data = data.randomSplit([0.8, 0.2], seed=1234)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.ml.evaluation import RegressionEvaluator

from pyspark.ml.regression import RandomForestRegressor

rf = RandomForestRegressor(featuresCol="features", labelCol="TotalQuantitySold")
model = rf.fit(train_data)


predictions = model.transform(test_data)
evaluator = RegressionEvaluator(labelCol="TotalQuantitySold", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Squared Error (RMSE): {rmse}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType
from datetime import datetime

# Initialize Spark session
spark = SparkSession.builder.appName("FutureDataExample").getOrCreate()

# Define the schema
schema = StructType([
    StructField("ProductID", IntegerType(), True),
    StructField("StoreID", StringType(), True),
    StructField("Date", DateType(), True),
    StructField("StockLevel", IntegerType(), True),
    StructField("TotalQuantitySold", IntegerType(), True),
    StructField("TotalQuantityShipped", IntegerType(), True),
    StructField("quantity_in_stock", IntegerType(), True),
    StructField("Year", IntegerType(), True),
    StructField("Month", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True)
])


# Read the sales_transactions.csv into a Spark DataFrame
future_data = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Demand_Forecasting_Sales_Analysis"
)
# Create a list of Rows with hardcoded data


#data = [
 #   Row(ProductID=101, StoreID=1, Date=datetime(2025, 4, 10), StockLevel=110, TotalQuantityShipped=0, Year=2025, Month=4, DayOfWeek=5),
 #   Row(ProductID=102, StoreID=2, Date=datetime(2025, 4, 11), StockLevel=160, TotalQuantityShipped=0, Year=2025, Month=4, DayOfWeek=6),
  #  Row(ProductID=103, StoreID=1, Date=datetime(2025, 4, 12), StockLevel=210, TotalQuantityShipped=0, Year=2025, Month=4, DayOfWeek=7)
#]

# Create DataFrame
#future_data = spark.createDataFrame(demand_df, schema)


# Select the required columns from demand_df
selected_columns = ["product_id", "store_id", "Date", "StockLevel", "quantity_in_stock", "TotalQuantityShipped", "Year", "Month", "DayOfWeek"]

# Create a new DataFrame with only the selected columns
filtered_demand_df = future_data.select(*selected_columns)

# Show the selected data
filtered_demand_df.show()


# Show the DataFrame
filtered_demand_df.show()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

future_data = assembler.transform(filtered_demand_df)
forecast = model.transform(future_data)
final_forecast = forecast.select("product_id", "store_id", "Date", "year", "DayOfWeek", "month", "prediction")

# Define Lakehouse Delta Table Path
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Demand_Predictions"  

# Step 4: Save Cleaned Inventory Data to the Lakehouse as a Delta Table
final_forecast.write.format("delta").mode("overwrite").save(table_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
