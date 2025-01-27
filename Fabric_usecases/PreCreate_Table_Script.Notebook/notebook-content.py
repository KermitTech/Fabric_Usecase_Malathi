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
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType
from delta.tables import DeltaTable

# Initialize Spark session
spark = SparkSession.builder \
    .appName("DeltaLakeIntegration") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Initialize the table paths
Tmp_organization_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Organisation"
organization_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Organisation"
Tmp_contact_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Contact"
contact_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Contact"
Tmp_opportunities_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Tmp_Opportunities"
opportunities_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Opportunities"
control_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Tables/salesforce/Control_Table"
stg_org_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Silver_Layer.Lakehouse/Tables/Salesforce_CRM/staging_organisation"

# Define function to create Delta table if it doesn't exist
def create_delta_table_if_not_exists(table_path, schema):
    # Check if the table already exists by trying to read from the location
    try:
        df = spark.read.format("delta").load(table_path)
        print(f"Table already exists at {table_path}. Skipping creation.")
    except Exception as e:
        # If table does not exist, create it by writing an empty DataFrame to the path
        print(f"Table does not exist at {table_path}. Creating table.")
        empty_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)
        empty_df.write.format("delta").mode("overwrite").save(table_path)
        print(f"Table created successfully at {table_path}.")

# Define the schema for each table in SQL format

# Organization table schema

organization_schema_sql = """
    Account_Name STRING,
    Phone STRING,
    Account_Owner_Name STRING,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

#Temporary Organization table schema

Tmp_organization_schema_sql = """
    Account_Name STRING,
    Phone STRING,
    Account_Owner_Name STRING,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

#Staging Organization table schema

stg_organization_schema_sql = """
    Account_Name STRING,
    Phone STRING,
    Account_Owner_Name STRING,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

# Temporary Contact table schema

Tmp_contact_schema_sql = """
    FirstName STRING,
    LastName STRING,
    Account_Name STRING,
    Title STRING,
    LastActivityDate TIMESTAMP,
    Email STRING,
    Phone STRING,
    MobilePhone STRING,
    MailingState STRING,
    MailingCountry STRING,
    Account_Owner_Name STRING,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""


# Contact table schema

contact_schema_sql = """
    FirstName STRING,
    LastName STRING,
    Account_Name STRING,
    Title STRING,
    LastActivityDate TIMESTAMP,
    Email STRING,
    Phone STRING,
    MobilePhone STRING,
    MailingState STRING,
    MailingCountry STRING,
    Account_Owner_Name STRING,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

# Temporary Opportunities table schema
Tmp_opportunities_schema_sql = """
    Opportunity_Name STRING,
    Amount STRING,
    Account_Name STRING,
    Probability STRING,
    Owner_Name STRING,
    CreatedDate TIMESTAMP,
    LastModifiedBy_Name STRING,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

# Opportunities table schema
opportunities_schema_sql = """
    Opportunity_Name STRING,
    Amount STRING,
    Account_Name STRING,
    Probability STRING,
    Owner_Name STRING,
    CreatedDate TIMESTAMP,
    LastModified TIMESTAMP,
    LastModifiedBy_Name STRING,
    UpdatedDate TIMESTAMP,
    UpdatedBy STRING,
    Batch_id INT,
    Load_Type STRING
"""

# Control table schema
control_table_schema_sql = """
    TableName STRING,
    MaxValue TIMESTAMP,
    BatchValue INT,
    LastUpdated TIMESTAMP,
    LastUpdatedBy STRING
"""

# Create the tables
create_delta_table_if_not_exists(organization_table_path, organization_schema_sql)
create_delta_table_if_not_exists(Tmp_organization_table_path, Tmp_organization_schema_sql)
create_delta_table_if_not_exists(stg_org_table_path, stg_organization_schema_sql)
create_delta_table_if_not_exists(Tmp_contact_table_path, Tmp_contact_schema_sql)
create_delta_table_if_not_exists(contact_table_path, contact_schema_sql)
create_delta_table_if_not_exists(Tmp_opportunities_table_path, Tmp_opportunities_schema_sql)
create_delta_table_if_not_exists(opportunities_table_path, opportunities_schema_sql)
create_delta_table_if_not_exists(control_table_path, control_table_schema_sql)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
