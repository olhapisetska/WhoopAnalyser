import os
import json
from datetime import datetime
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
start_date = datetime(2024, 12, 13).isoformat() + "Z"  # fixed start
end_date = datetime.utcnow().isoformat() + "Z"         # dynamic end (today)

print(f"📡 Fetching workouts from {start_date} to {end_date}...")
workouts = client.get_workout_collection(start=start_date, end=end_date)

with open("workouts.json", "w") as f:
    json.dump(workouts, f, indent=4)

print(f"✅ Found {len(workouts)} workouts and saved them to workouts.json")
