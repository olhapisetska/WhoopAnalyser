import os
import json
from dotenv import load_dotenv
from whoop_client import WhoopClient

# Load environment variables from .env
load_dotenv()

# Get credentials from .env file
client_id = os.getenv("WHOOP_CLIENT_ID")
client_secret = os.getenv("WHOOP_CLIENT_SECRET")
redirect_uri = os.getenv("WHOOP_REDIRECT_URI")

if not client_id or not client_secret:
    raise ValueError("WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET must be set in your .env file")

# Initialize client
client = WhoopClient(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
)

# Step 1: Direct user to authorization URL
print("👉 Go to this URL in your browser and log in:")
print(client.get_authorization_url())

# Step 2: User pastes redirect URL after login
authorization_response = input("\nPaste the FULL redirect URL you were sent to: ")

# Step 3: Exchange code for token
token = client.fetch_token(authorization_response)

# Save token for reuse
with open("token.json", "w") as f:
    json.dump(token, f, indent=2)
print("✅ Access token saved to token.json")

# Step 4: Fetch workouts and save to file
workouts = client.get_workout_collection()

with open("workouts.json", "w") as f:
    json.dump(workouts, f, indent=2)

print(f"✅ Saved {len(workouts.get('records', []))} workouts to workouts.json")
