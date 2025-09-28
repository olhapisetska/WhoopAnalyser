import os
import json
from dotenv import load_dotenv
from whoop_client import WhoopClient

# Load environment variables from .env
load_dotenv()

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    raise ValueError("❌ Missing WHOOP credentials in .env (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)")

# Initialize client
client = WhoopClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)

# Try to load existing token
token = client.load_token()

if not token:
    # Step 1: Direct user to authorization URL
    auth_url, state = client.create_authorization_url()
    print("👉 Go to this URL in your browser and log in:")
    print(auth_url)

    # Step 2: Paste the redirect URL after login
    redirect_response = input("\nPaste the FULL redirect URL you were sent to: ").strip()

    # Step 3: Fetch token
    token = client.fetch_token(redirect_response)

# --- Fetch WHOOP data --- #
print("📡 Fetching WHOOP data...")

profile = client.get_profile()
workouts = client.get_workout_collection()
sleep = client.get_sleep_collection()
recovery = client.get_recovery_collection()

# --- Save results to JSON --- #
with open("profile.json", "w") as f:
    json.dump(profile, f, indent=2)
with open("workouts.json", "w") as f:
    json.dump(workouts, f, indent=2)
with open("sleep.json", "w") as f:
    json.dump(sleep, f, indent=2)
with open("recovery.json", "w") as f:
    json.dump(recovery, f, indent=2)

print("✅ Data saved: profile.json, workouts.json, sleep.json, recovery.json")
