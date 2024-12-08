import csv
import requests
import json
import os

API_URL = "https://api-bcbe5a.stack.tryrelevance.com/latest/agents/trigger"
API_KEY = os.environ.get("API_KEY")  # Read from environment variable
AGENT_ID = "ad16dc57-e432-4db3-b0a0-262aacdce8dc"
CHUNK_SIZE = 1
CSV_FILE = "velocity_watchlist.csv"

def read_csv(file_path):
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def chunk_data(data, n):
    for i in range(0, len(data), n):
        yield data[i:i+n]

def build_payload(batch, agent_id):
    content_str = "\n".join([str(row) for row in batch])
    return {
        "message": {
            "role": "user",
            "content": content_str
        },
        "agent_id": agent_id
    }

def send_data(payload):
    resp = requests.post(
        API_URL,
        headers={"Content-Type": "application/json", "Authorization": API_KEY},
        data=json.dumps(payload)
    )
    return resp

def main():
    data = read_csv(CSV_FILE)
    for batch in chunk_data(data, CHUNK_SIZE):
        payload = build_payload(batch, AGENT_ID)
        response = send_data(payload)
        if response.status_code == 200:
            print("Successfully sent batch.")
        else:
            print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    main()