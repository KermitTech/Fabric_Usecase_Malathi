# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from flask import Flask, jsonify
import csv

# Initialize the Flask app
app = Flask(__name__)

# Load the campaign data from the CSV file
def load_campaign_data():
    campaign_data = []
    try:
        with open('abfss://Malathi@onelake.dfs.fabric.microsoft.com/Campaign_Bronze_Layer.Lakehouse/Files/campaigns/campaign_data.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                campaign_data.append({
                    "campaign_id": row["campaign_id"],
                    "campaign_name": row["campaign_name"],
                    "source": row["source"],
                    "medium": row["medium"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "clicks": int(row["clicks"]),
                    "impressions": int(row["impressions"]),
                    "conversions": int(row["conversions"]),
                    "revenue": float(row["revenue"]),
                    "campaign_cost": float(row["campaign_cost"])
                })
    except Exception as e:
        print(f"Error loading campaign data: {e}")
    return campaign_data

# Route to get all campaigns
@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    campaign_data = load_campaign_data()
    if campaign_data:
        return jsonify(campaign_data)
    else:
        return jsonify({"error": "No campaign data available"}), 500

# Route to get a single campaign by campaign_id
@app.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign_by_id(campaign_id):
    campaign_data = load_campaign_data()
    # Find the campaign based on the campaign_id
    campaign = next((item for item in campaign_data if item["campaign_id"] == campaign_id), None)
    if campaign:
        return jsonify(campaign)
    else:
        return jsonify({"error": "Campaign not found"}), 404

# Start the server
if __name__ == '__main__':
    # Bind the server to '0.0.0.0' to allow external access
    app.run(host='0.0.0.0', port=5000)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import requests

# Define the API URL
api_url = "http://localhost:5000/api/campaigns"  # Replace with your API URL

try:
    # Send a GET request to the API
    response = requests.get(api_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print("API Response:")
        for item in data:
            print(item)
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Error connecting to the API: {e}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
