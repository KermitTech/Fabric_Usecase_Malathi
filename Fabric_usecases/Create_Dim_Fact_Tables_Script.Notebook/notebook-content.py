# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Load cleansed Silver Layer tables

df_sales_data = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/dbo/cleansed_sales_data")
df_store_data = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/dbo/cleansed_store_data")
df_product_data = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/dbo/cleansed_product_data")

df_sales_data.show()
df_store_data.show()
df_product_data.show()

#To create dim_product table

df_store_data.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_store")


#To create dim_store table

df_product_data.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_product")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, date_format, dayofmonth, dayofweek, month, year, weekofyear, to_date


# Create Dim_Date
dim_date = df_sales_data.select(
    to_date(col("sale_date")).alias("sale_date"),  # Remove timestamp and keep only the date
    date_format(col("sale_date"), "EEEE").alias("day_name"),
    dayofmonth(col("sale_date")).alias("day_of_month"),
    dayofweek(col("sale_date")).alias("day_of_week"),
    month(col("sale_date")).alias("month"),
    year(col("sale_date")).alias("year"),
    weekofyear(col("sale_date")).alias("week_of_year")
).distinct()

dim_date.show()

dim_date.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_date")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Join to create Fact_Sales

df_dim_product = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_product")
df_dim_date = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_date")
df_dim_store = spark.read.format("delta").load("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/dim_store")


fact_sales = df_sales_data.alias("s") \
    .join(dim_date.alias("d"), to_date(col("s.sale_date")) == col("d.sale_date")) \
    .join(df_dim_product.alias("p"), col("s.product_id") == col("p.product_id")) \
    .join(df_dim_store.alias("st"), col("s.store_id") == col("st.store_id")) \
    .select(
        col("s.transaction_id"),
        col("d.sale_date").alias("date_key"),
        col("d.month").alias("month_key"),
        col("d.year").alias("year_key"),
        col("p.product_name").alias("product_key"),
        col("p.category").alias("category"),
        col("st.store_name").alias("store_key"),
        col("st.country").alias("country"),
        col("s.quantity"),
        col("s.unit_price"),
        col("s.discount"),
        col("s.sales_amount").alias("total_amount")
    )

fact_sales.show()

fact_sales.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/gold_layer/fact_sales")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
