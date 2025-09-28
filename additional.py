import os
import json
import webbrowser
from flask import Flask, request
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session

# Load env variables
load_dotenv()
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")

AUTH_URL = "https://api-7.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api-7.whoop.com/oauth/oauth2/token"

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code returned."

    # Exchange code for token
    client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    token = client.fetch_token(TOKEN_URL, code=code)

    with open("token.json", "w") as f:
        json.dump(token, f, indent=4)

    return "✅ Login successful! You can close this tab now."

if __name__ == "__main__":
    client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    authorization_url, _ = client.create_authorization_url(AUTH_URL)

    print("🔗 Open this link to log in:", authorization_url)
    webbrowser.open(authorization_url)

    app.run(port=8000)
