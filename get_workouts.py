import json
from whoop import WhoopClient

username = "USERNAME"
password = "PASSWORD"

start_date="2025-01-01 23:59:59.999999"

print("Get workouts...")
with WhoopClient(username, password) as client:
    workouts = client.get_workout_collection(start_date=start_date)

with open("workouts.json", "w") as f:
    json.dump(workouts, f, indent=4)

print(f"Found {len(workouts)} workouts and saved it to `workouts.json`")