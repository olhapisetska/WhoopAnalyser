import os
import json
import secrets
import string
import requests
from authlib.integrations.requests_client import OAuth2Session

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
BASE_URL = "https://api.prod.whoop.com/developer/v2"

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"


class WhoopClient:
    def __init__(self):
        self.session = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="offline read:profile read:workout read:sleep read:recovery",
            code_challenge_method="S256",
        )
        self.state = None
        self.code_verifier = None

        # Try to load token if already saved
        if os.path.exists("token.json"):
            with open("token.json", "r") as f:
                token = json.load(f)
            self.session.token = token

    def create_authorization_url(self):
        uri, state = self.session.create_authorization_url(
            AUTH_URL, code_verifier=self._gen_code_verifier()
        )
        self.state = state
        return uri

    def fetch_token(self, authorization_response):
        token = self.session.fetch_token(
            url=TOKEN_URL,
            authorization_response=authorization_response,
            code_verifier=self.code_verifier,
        )
        with open("token.json", "w") as f:
            json.dump(token, f)
        self.session.token = token
        return token

    def _gen_code_verifier(self):
        alphabet = string.ascii_letters + string.digits + "-._~"
        self.code_verifier = "".join(secrets.choice(alphabet) for _ in range(64))
        return self.code_verifier

    # -------- API calls -------- #
    def get_profile(self):
        resp = self.session.get(f"{BASE_URL}/user/profile/basic")
        resp.raise_for_status()
        return resp.json()

    def get_workout_collection(self, start=None, end=None):
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(f"{BASE_URL}/activity/workout", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_sleep_collection(self, start=None, end=None):
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(f"{BASE_URL}/activity/sleep", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_recovery_collection(self, start=None, end=None):
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        resp = self.session.get(f"{BASE_URL}/recovery", params=params)
        resp.raise_for_status()
        return resp.json()
