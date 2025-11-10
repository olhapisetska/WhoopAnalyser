
import os
import json
import time
import csv
from datetime import datetime
from collections import defaultdict
from whoop_client import WhoopClient
# ---------------- CONFIG ---------------- #
START_DATE = datetime(2024, 12, 13).isoformat() + "Z"
END_DATE = datetime.utcnow().isoformat() + "Z"
MAX_WORKOUTS = 1000  # Limit to 100 workouts
OUTPUT_JSON = "workouts.json"
OUTPUT_CSV = "workouts.csv"
OUTPUT_SUMMARY = "workouts_summary.json"
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
# ---------------- FETCH WORKOUTS ---------------- #
print(f"📡 Fetching workouts from {START_DATE} to {END_DATE} (max {MAX_WORKOUTS})...")
all_workouts = []
next_token = None
base_url = "https://api.prod.whoop.com/developer/v2/activity/workout"
try:
    while True:
        params = {"start": START_DATE, "end": END_DATE}
        if next_token:
            params["next_token"] = next_token
        resp = client.session.get(base_url, params=params)
        if resp.status_code == 429:
            print("⚠️ Rate limit hit — sleeping for 30 seconds...")
            time.sleep(30)
            continue
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        all_workouts.extend(records)
        print(f"📥 Retrieved {len(records)} workouts (total so far: {len(all_workouts)})")
        # Stop if we reach the max limit
        if len(all_workouts) >= MAX_WORKOUTS:
            all_workouts = all_workouts[:MAX_WORKOUTS]  # Trim extra if needed
            break
        next_token = data.get("next_token")
        if not next_token:
            break
        time.sleep(1)  # small pause to avoid hitting rate limit
except KeyboardInterrupt:
    print("\n⚠️ Fetch interrupted by user. Partial results saved to JSON.")
print(f"✅ Finished fetching. Total workouts: {len(all_workouts)}")
# ---------------- SAVE FULL JSON ---------------- #
with open(OUTPUT_JSON, "w") as f:
    json.dump(all_workouts, f, indent=4)
# ---------------- SAVE CSV ---------------- #
if all_workouts:
    keys = set()
    for wo in all_workouts:
        keys.update(wo.keys())
    keys = list(keys)
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for wo in all_workouts:
            row = dict(wo)
            score = row.pop("score", {})
            # Flatten score
            for k, v in score.items():
                if k == "zone_durations" and isinstance(v, dict):
                    for z, z_val in v.items():
                        row[f"score_{z}"] = z_val
                else:
                    row[f"score_{k}"] = v
            writer.writerow(row)
# ---------------- CREATE SUMMARY JSON ---------------- #
workout_counts = defaultdict(int)
for wo in all_workouts:
    sport_name = wo.get("sport_name", f"Unknown ({wo.get('sport_id')})")
    workout_counts[sport_name] += 1
summary = {
    "total_workouts": len(all_workouts),
    "by_activity": dict(workout_counts)
}
with open(OUTPUT_SUMMARY, "w") as f:
    json.dump(summary, f, indent=4)
print(f"📊 Saved summary to {OUTPUT_SUMMARY}")
