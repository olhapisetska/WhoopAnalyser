import os
from whoop_client import WhoopClient

# Load client credentials from environment variables
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"

client = WhoopClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)

# Try loading an existing token
token = client.load_token()

if not token:
    # Step 1: Generate login URL
    auth_url, state = client.create_authorization_url()
    print("👉 Go to this URL in your browser and log in:")
    print(auth_url)

    # Step 2: Paste redirect URL
    redirect_response = input("\nPaste the FULL redirect URL you were sent to: ")

    # Step 3: Exchange code for token
    token = client.fetch_token(redirect_response)

print("📡 Fetching WHOOP data...")

# Example API calls
profile = client.get_profile()
print("\n=== Profile ===")
print(profile)

workouts = client.get_workout_collection()
print("\n=== Workouts ===")
print(workouts)

sleep = client.get_sleep_collection()
print("\n=== Sleep ===")
print(sleep)

recovery = client.get_recovery_collection()
print("\n=== Recovery ===")
print(recovery)
