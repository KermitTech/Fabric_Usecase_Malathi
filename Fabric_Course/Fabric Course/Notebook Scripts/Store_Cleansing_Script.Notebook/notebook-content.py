# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql.functions import col, regexp_replace, udf, initcap
from pyspark.sql.types import FloatType, StringType
from pyspark.sql.types import BooleanType
from pyspark.sql import functions as F
import requests
from pyspark.sql.functions import col, when, lit, round
import json


# Read data from Lakehouse table
store_df = spark.read.format("delta").load(
    "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/Supply_Chain/raw_store"
)

# Before cleansing
store_df.show()

# Function to standardize common address abbreviations
def standardize_address(address):
    address = F.regexp_replace(address, r'\bavenue\b', 'Ave')
    address = F.regexp_replace(address, r'\bStreet\b', 'St')
    address = F.regexp_replace(address, r'\broad\b', 'Rd')
    address = F.regexp_replace(address, r'\blane\b', 'Ln')
    address = F.regexp_replace(address, r'\bdrive\b', 'Dr')
    address = F.regexp_replace(address, r'\bcourt\b', 'Ct')
    return address


#  data cleansing steps

# To cleanse address


#Standardize case
store_df = store_df.withColumn('address_line1', initcap(F.col('address_line1')))

# Apply abbreviation function to the address column
store_df = store_df.withColumn('address_line1', standardize_address(F.col('address_line1')))

#Handling internal spacing
store_df = store_df.withColumn('address_line1', F.regexp_replace(F.col('address_line1'), r'\s+', ' '))


# Optionally, trim spaces and convert to proper case
store_df = store_df.withColumn('address_line1', F.trim(F.col('address_line1')))

# Validate address format: Ensure 'address_line1' is not null or empty
store_df = store_df.filter(F.col('address_line1').isNotNull() & (F.col('address_line1') != ""))


# Fill missing store manager information
store_df = store_df.fillna({'store_manager': 'Unknown'})


# Define conditions for a valid postal code
def is_valid_postal_code(postal_code):
    if postal_code is None:
        return False
    # Remove spaces
    postal_code = postal_code.strip()
    # Check length between 4 and 10
    if 4 <= len(postal_code) <= 10:
        # Valid 4-10 digit postal code or ZIP+4 format
        if postal_code.isdigit():  # All digits
            return True
        elif len(postal_code) == 10 and postal_code[:5].isdigit() and postal_code[6:].isdigit() and postal_code[5] == '-':  # ZIP+4
            return True
    return False

# Register the function as a UDF
is_valid_postal_code_udf = F.udf(is_valid_postal_code, BooleanType())

# Apply the condition to filter valid postal codes
store_df = store_df.filter(is_valid_postal_code_udf(F.col('postal_code')))


# Show the cleaned DataFrame
store_df.show()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import time
import requests
from pyspark.sql.functions import col, when, round

# Define the function to fetch coordinates
def get_coordinates(address, use_user_agent=True):
    try:
        # If using User-Agent, include it in the headers
        headers = {}
        if use_user_agent:
            headers = {
                'User-Agent': 'MyAPIClient/1.0 (no-reply@domain.com)'  # You can replace this with your own name/email
            }

        # Call the Nominatim API with or without the custom User-Agent
        response = requests.get(f"https://nominatim.openstreetmap.org/search?q={address}&format=json&addressdetails=1", headers=headers)
        
        # Check the response status code
        if response.status_code == 403:
            print(f"Error: 403 Forbidden. Check your User-Agent and rate limits.")
            return None, None
        elif response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            return None, None
        
        data = response.json()
        
        if data:
            # Extract latitude and longitude from the first result
            latitude = data[0].get('lat')
            longitude = data[0].get('lon')
            print(f"Found coordinates: Latitude={latitude}, Longitude={longitude}")
            return float(latitude) if latitude else None, float(longitude) if longitude else None
        else:
            print(f"No data found for address: {address}")
            return None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None

# Fetch missing latitude and longitude locally
def fetch_missing_coordinates(df, use_user_agent=True):
    missing_rows = df.filter(col("latitude").isNull() | col("longitude").isNull()).collect()
    updates = []
    for row in missing_rows:
        # Construct the full address only if latitude or longitude is missing
        if row['latitude'] is None or row['longitude'] is None:
            address = f"{row['address_line1']}, {row['state']}, {row['postal_code']}, {row['country']}"
            lat, lon = get_coordinates(address, use_user_agent)
            if lat is not None and lon is not None:
                updates.append((row['store_id'], lat, lon))
            
            # Add a delay to avoid hitting the rate limit (Nominatim suggests 1 request per second)
            time.sleep(1)
    
    return updates

# Collect rows with missing latitude or longitude
missing_updates = fetch_missing_coordinates(store_df, use_user_agent=True)  # Set False to test without User-Agent

# Create a DataFrame with updated coordinates
if missing_updates:
    updates_df = spark.createDataFrame(missing_updates, schema=["store_id", "latitude", "longitude"])

    # Rename latitude and longitude in updates_df to avoid ambiguity
    updates_df = updates_df.withColumnRenamed("latitude", "latitude_new") \
                           .withColumnRenamed("longitude", "longitude_new")

    # Perform the join and handle ambiguous column names by renaming them
    store_df = store_df.join(updates_df, on="store_id", how="left_outer") \
        .withColumn("latitude", when(col("latitude").isNull(), col("latitude_new")).otherwise(col("latitude"))) \
        .withColumn("longitude", when(col("longitude").isNull(), col("longitude_new")).otherwise(col("longitude"))) \
        .drop("latitude_new", "longitude_new")

# Assuming 'store_df' already has updated latitude and longitude values
store_df = store_df.withColumn("latitude", round(col("latitude"), 4)) \
                   .withColumn("longitude", round(col("longitude"), 4))

# Show the updated DataFrame
store_df.show(truncate=False)

# Define the output path or table name for your Delta table
table_name = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver.Lakehouse/Tables/Supply_Chain/Cleansed_store"  # Example of a table name

# Save the DataFrame as a Delta table
store_df.write.format("delta").mode("overwrite").save(table_name)



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
