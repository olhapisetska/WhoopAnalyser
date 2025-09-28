import os
import secrets
import string
import base64
import hashlib
from authlib.integrations.requests_client import OAuth2Session

# WHOOP OAuth2 endpoints
AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API_BASE_URL = "https://api.prod.whoop.com"

class WhoopClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # PKCE (Proof Key for Code Exchange)
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge(self.code_verifier)

        # OAuth2 session
        self.session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope="offline read:profile read:workout read:sleep read:recovery"
        )

    def _generate_code_verifier(self, length: int = 128) -> str:
        charset = string.ascii_letters + string.digits + "-._~"
        return "".join(secrets.choice(charset) for _ in range(length))

    def _generate_code_challenge(self, code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    def get_authorization_url(self) -> str:
        uri, state = self.session.create_authorization_url(
            AUTH_URL,
            code_challenge=self.code_challenge,
            code_challenge_method="S256"
        )
        self.state = state
        return uri

    def fetch_token(self, authorization_response: str) -> dict:
        """Exchange authorization code for access + refresh token"""
        token = self.session.fetch_token(
            url=TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret,
            code_verifier=self.code_verifier,
            client_secret_post=True  # 👈 fixes invalid_client
        )
        return token

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token"""
        new_token = self.session.refresh_token(
            url=TOKEN_URL,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            client_secret_post=True
        )
        return new_token

    def get_profile(self) -> dict:
        resp = self.session.get(f"{API_BASE_URL}/developer/v1/user")
        resp.raise_for_status()
        return resp.json()

    def get_workout_collection(self) -> dict:
        resp = self.session.get(f"{API_BASE_URL}/developer/v1/workout")
        resp.raise_for_status()
        return resp.json()

    def get_sleep_collection(self) -> dict:
        resp = self.session.get(f"{API_BASE_URL}/developer/v1/sleep")
        resp.raise_for_status()
        return resp.json()

    def get_recovery_collection(self) -> dict:
        resp = self.session.get(f"{API_BASE_URL}/developer/v1/recovery")
        resp.raise_for_status()
        return resp.json()
