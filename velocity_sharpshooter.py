import asyncio
import aiohttp
import csv
import json
import os

# Adjustable variables
API_URL = "https://api-bcbe5a.stack.tryrelevance.com/latest/agents/trigger"
API_KEY = os.environ.get("API_KEY")
AGENT_ID = "aed7c332-6a24-4f09-a017-105e869f9fd7"
DEFAULT_LOOKBACK_DAYS = 7
file_path = "velocity_watchlist.csv"
PROJECT_ID = "07e6685bed59-490f-aa03-8fcb7089c43f"
REGION = "bcbe5a"
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")

def create_payload(row, lookback_days):
    """Creates the API payload for a given row of data."""
    content = json.dumps({
        "data": {
            "Full Name": f"{row['First Name']} {row['Last Name']}",
            "Title": row.get("Title", ""),
            "Company": row.get("Company", ""),
            "Email": row.get("Email", ""),
            "LinkedIn URL": row.get("Person Linkedin Url", "")
        },
        "lookback_days": lookback_days,
        "google_sheet_id": GOOGLE_SHEET_ID
    })
    return {
        "message": {
            "role": "user",
            "content": content
        },
        "agent_id": AGENT_ID
    }

async def send_request(session, payload):
    """Sends a POST request to the Relevance agent API."""
    try:
        headers = {
            "Authorization": f"{PROJECT_ID}:{API_KEY}:{REGION}",
            "Content-Type": "application/json"
        }
        async with session.post(API_URL, json=payload, headers=headers) as response:
            if response.status != 200:
                error = await response.text()
                return {"error": error, "payload": payload}
            return None
    except Exception as e:
        return {"error": str(e), "payload": payload}

async def process_csv(file_path, lookback_days=DEFAULT_LOOKBACK_DAYS):
    """Processes a CSV file and sends data to the Relevance agent API asynchronously."""
    errors = []

    async with aiohttp.ClientSession() as session:
        tasks = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                payload = create_payload(row, lookback_days)
                tasks.append(send_request(session, payload))

        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                errors.append(result)

    return errors

if __name__ == "__main__":
    errors = asyncio.run(process_csv(file_path))

    if errors:
        print("Errors occurred during API calls:")
        for error in errors:
            print(error)
    else:
        print("All API calls completed successfully.")
