import os
import json
import secrets
import string
from authlib.integrations.requests_client import OAuth2Session

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API_BASE_URL = "https://api.prod.whoop.com/developer/v2"


class WhoopClient:
    def __init__(self, client_id, client_secret, redirect_uri, scope=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or "offline read:profile read:workout read:sleep read:recovery"

        # Generate PKCE code_verifier
        self.code_verifier = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(64)
        )

        # OAuth2 session
        self.session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            code_challenge_method="S256",
            code_verifier=self.code_verifier,
        )

    def create_authorization_url(self):
        uri, state = self.session.create_authorization_url(AUTH_URL)
        return uri, state

    def fetch_token(self, authorization_response):
        token = self.session.fetch_token(
            url=TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret,
            code_verifier=self.code_verifier,
        )
        with open("token.json", "w") as f:
            json.dump(token, f, indent=2)
        print("✅ Access token saved to token.json")
        return token

    def load_token(self):
        if os.path.exists("token.json"):
            with open("token.json", "r") as f:
                token = json.load(f)
            self.session.token = token
            return token
        return None

    # -------- WHOOP v2 API endpoints -------- #

    def get_profile(self, full=False):
        """Get user profile (basic or full)."""
        url = f"{API_BASE_URL}/user/profile"
        if not full:
            url += "/basic"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_workout_collection(self, start=None, end=None):
        """Get workouts (optionally with start/end dates)."""
        url = f"{API_BASE_URL}/activity/workout"
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_sleep_collection(self, start=None, end=None):
        """Get sleep data (optionally with start/end dates)."""
        url = f"{API_BASE_URL}/activity/sleep"
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_recovery_collection(self, start=None, end=None):
        """Get recovery data (optionally with start/end dates)."""
        url = f"{API_BASE_URL}/recovery"
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
