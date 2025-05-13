# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from delta.tables import DeltaTable


# === CONFIGURATION ===
bronze_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/bronze/Opportunity"
silver_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/silver/Opportunity"
gold_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/gold/Opportunity"
temp_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/bronze/Opportunity_temp"
backup_table_path = f"abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/gold/Opportunity_backup"
log_table_path = "abfss://Malathi@onelake.dfs.fabric.microsoft.com/Bronze.Lakehouse/Tables/gold/Load_Auditlogs"

# === INIT LOG VARIABLES ===
log_time = datetime.now()
log_operation = "Opportunity Data Load"
log_status = "Started"

bronze_count = 0
silver_count = 0
gold_count = 0

# === START LOAD PROCESS ===
try:
    # === READ BRONZE COUNT (logging only) ===
    try:
        bronze_df = spark.read.format("delta").load(bronze_table_path)
        bronze_count = bronze_df.count()
    except:
        print("⚠️ Could not read Bronze table — skipping count.")

    # === READ SILVER TABLE ===
    silver_df = spark.read.format("delta").load(silver_table_path)
    silver_count = silver_df.count()

    if silver_count == 0:
        log_status = "Skipped (Silver empty) or check the given filepath is correct or not"
        print("⚠️ Silver table is empty — skipping Gold update.")
            # Attempt to read current Gold table count for logging
        try:
            gold_df_pre = spark.read.format("delta").load(gold_table_path)
            gold_count = gold_df_pre.count()
            print(f"Existing Gold count: {gold_count}")
        except:
            print("⚠️ Could not read Gold table for count.")
    elif bronze_count == 0:
        log_status = "No Data in Bronze or check the given filepath is correct or not"
        print("⚠️ Bronze table has 0 rows — stopping further load.")
            # Attempt to read current Gold table count for logging
        try:
            gold_df_pre = spark.read.format("delta").load(gold_table_path)
            gold_count = gold_df_pre.count()
            print(f"Existing Gold count: {gold_count}")
        except:
            print("⚠️ Could not read Gold table for count.")
    else:
        print(f"✅ Silver has {silver_count} rows — proceeding with Gold update.")

        # === BACKUP GOLD TABLE IF EXISTS ===
        try:
            gold_df = spark.read.format("delta").load(gold_table_path)
            gold_df.write.mode("overwrite").format("delta").save(backup_table_path)
            print(f"✅ Backup of Gold table saved to: {backup_table_path}")
        except:
            print("Gold table not found — assuming first run, skipping backup.")

        # === OVERWRITE GOLD TABLE WITH SILVER DATA ===
        silver_df.write.mode("overwrite").format("delta").save(gold_table_path)
        print("✅ Gold table overwritten successfully.")
        log_status = "Success"

        # === FINAL GOLD COUNT ===
        try:
            gold_df_final = spark.read.format("delta").load(gold_table_path)
            gold_count = gold_df_final.count()
        except:
            print("⚠️ Could not count rows in new Gold table.")
            log_status = " Could not count rows in new Gold table."

except Exception as e:
    log_status = f"Failed: {e}"
    print(f"❌ Pipeline failure: {e}")

# === PREPARE LOG RECORD ===
log_data = [(log_time, log_operation, log_status, bronze_count, silver_count, gold_count)]
log_schema = ["timestamp", "operation", "status", "bronze_count", "silver_count", "gold_count"]

log_df = spark.createDataFrame(log_data, log_schema)

# === WRITE LOG ENTRY ===
try:
    log_df.write.mode("append").format("delta").save(log_table_path)
    print(f"✅ Log written to: {log_table_path}")
except Exception as e:
    print(f"⚠️ Failed to write log: {e}")

# Load Delta table
log_table = DeltaTable.forPath(spark, log_table_path)

# Delete records older than 15 days
log_table.delete("timestamp < current_timestamp() - INTERVAL 15 DAYS")

#log_table.delete("timestamp < TIMESTAMP '2025-05-10 00:00:00'")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
