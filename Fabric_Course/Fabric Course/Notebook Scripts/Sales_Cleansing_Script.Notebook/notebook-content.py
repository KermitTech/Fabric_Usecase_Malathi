# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql.functions import col


# Read the sales_transactions.csv into a Spark DataFrame
sales_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_sales"
)
sales_df.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.functions import to_timestamp

# Sample cleaning logic function
def clean_sales_data(df):
    # 1. Remove duplicates based on 'transaction_id'
    df = df.dropDuplicates(['transaction_id'])

    # Filter out the transaction_id which is not null
    df=df.filter(col("transaction_id").isNotNull())
    
    # 2. Handle missing values (fill with defaults for specific columns)
    df = df.fillna({
        'quantity': 0,
        'unit_price': 0,
        'discount': 0,
        'sales_amount': 0  # Assuming you want to fill sales_amount too
    })

    # Filter out the sale_date which is not null
    df=df.filter(col("sale_date").isNotNull())

    # 3. Validate date formats: Convert 'sale_date' to timestamp type
    df = df.withColumn('sale_date', to_timestamp('sale_date'))
    
    # 4. Remove transactions with invalid amounts (e.g., unit_price <= 0)
    df = df.filter(df.unit_price > 0)
    
    # 5. Handle missing or invalid 'quantity' and 'sales_amount'
    df = df.filter((df.quantity > 0) & (df.sales_amount > 0))
    
    return df

# Assuming 'sales_df' is the DataFrame containing your sales data
# Call the cleaning function
cleaned_sales_df = clean_sales_data(sales_df)

# Show the cleaned data
cleaned_sales_df.show(truncate=False)

#To write output in csv file
#output_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Files/cleansed_files/cleaned_sales_data.csv"
#cleaned_sales_df.write.option("header", "true").mode("overwrite").csv(output_path)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_sales"  # Example of a table name

# Save the DataFrame as a Delta table
cleaned_sales_df.write.format("delta").mode("overwrite").save(table_name)


# Coalesce to write all data into a single CSV file
#cleaned_sales_df.coalesce(1).write.option("header", "true").csv(output_path)



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
