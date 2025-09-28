import os
import json
from datetime import datetime, timezone
from whoop_client import WhoopClient

# Load credentials from environment
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")

# Initialize client
client = WhoopClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)
client.load_token()  # Load saved token.json

# Define date range
START_DATE = datetime(2024, 12, 13, tzinfo=timezone.utc)
END_DATE = datetime.now(timezone.utc)  # today

def filter_workouts(workouts, start_date, end_date):
    """Filter workouts by start/end datetime range"""
    filtered = []
    for workout in workouts.get("records", []):  # your data is inside "records"
        start_time = datetime.fromisoformat(workout["start"].replace("Z", "+00:00"))
        if start_date <= start_time <= end_date:
            filtered.append(workout)
    return filtered

print("📡 Fetching workouts from Whoop API...")
raw_workouts = client.get_workout_collection(start=START_DATE.isoformat())

print("🪄 Filtering workouts...")
filtered_workouts = filter_workouts(raw_workouts, START_DATE, END_DATE)

# Save results
output_file = "filtered_workouts.json"
with open(output_file, "w") as f:
    json.dump(filtered_workouts, f, indent=4)

print(f"✅ Saved {len(filtered_workouts)} workouts to {output_file}")
