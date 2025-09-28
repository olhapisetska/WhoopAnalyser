import os
import json
import secrets
import string
import requests
from urllib.parse import urlencode
from authlib.integrations.requests_client import OAuth2Session

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API_BASE_URL = "https://api.prod.whoop.com/developer/v1"

class WhoopClient:
    def __init__(self, client_id, client_secret, redirect_uri, scope=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or "offline read:profile read:workout read:sleep read:recovery"

        # Generate code_verifier + code_challenge for PKCE
        self.code_verifier = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
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

    def get_profile(self):
        url = f"{API_BASE_URL}/user"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_workout_collection(self):
        url = f"{API_BASE_URL}/activity"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_sleep_collection(self):
        url = f"{API_BASE_URL}/sleep"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_recovery_collection(self):
        url = f"{API_BASE_URL}/recovery"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
