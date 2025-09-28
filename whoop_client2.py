from __future__ import annotations

import os
import secrets
import string
import base64
import hashlib
from datetime import datetime, time, timedelta
from typing import Any

from authlib.integrations.requests_client import OAuth2Session


# WHOOP v2 endpoints
AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
REQUEST_URL = "https://api.prod.whoop.com"


class WhoopClient:
    """
    WHOOP v2 API Client using OAuth2 Authorization Code Flow with PKCE.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: list[str] | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or [
            "offline",
            "read:profile",
            "read:workout",
            "read:sleep",
            "read:recovery",
        ]

        self.session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
        )

        # PKCE setup
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge(self.code_verifier)

    # ----------------------------------------------------------------------
    # OAuth2 FLOW
    # ----------------------------------------------------------------------

    def get_authorization_url(self) -> str:
        """Generate WHOOP authorization URL to direct the user to."""
        uri, state = self.session.create_authorization_url(
            AUTH_URL,
            code_challenge=self.code_challenge,
            code_challenge_method="S256",
        )
        return uri

    def fetch_token(self, authorization_response: str) -> dict[str, Any]:
        """
        Exchange the authorization code for an access token.

        Args:
            authorization_response (str): Full callback URL containing ?code=...
        """
        token = self.session.fetch_token(
            url=TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret,
            code_verifier=self.code_verifier,
        )
        return token

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh the access token using the refresh_token."""
        token = self.session.refresh_token(
            url=TOKEN_URL,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        return token

    # ----------------------------------------------------------------------
    # API CALLS
    # ----------------------------------------------------------------------

    def get_profile(self) -> dict[str, Any]:
        return self._make_request("GET", "v2/user/profile/basic")

    def get_body_measurement(self) -> dict[str, Any]:
        return self._make_request("GET", "v2/user/measurements/body")

    def get_sleep_by_id(self, sleep_uuid: str) -> dict[str, Any]:
        return self._make_request("GET", f"v2/activity/sleep/{sleep_uuid}")

    def get_sleep_collection(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict[str, Any]]:
        start, end = self._format_dates(start_date, end_date)
        return self._make_paginated_request(
            "GET", "v2/activity/sleep", params={"start": start, "end": end, "limit": 25}
        )

    def get_workout_by_id(self, workout_uuid: str) -> dict[str, Any]:
        return self._make_request("GET", f"v2/activity/workout/{workout_uuid}")

    def get_workout_collection(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict[str, Any]]:
        start, end = self._format_dates(start_date, end_date)
        return self._make_paginated_request(
            "GET", "v2/activity/workout", params={"start": start, "end": end, "limit": 25}
        )

    def get_recovery_for_sleep(self, sleep_uuid: str) -> dict[str, Any]:
        """Recoveries in v2 are tied to sleep UUIDs."""
        return self._make_request("GET", f"v2/activity/sleep/{sleep_uuid}/recovery")

    def get_recovery_collection(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict[str, Any]]:
        start, end = self._format_dates(start_date, end_date)
        return self._make_paginated_request(
            "GET", "v2/recovery", params={"start": start, "end": end, "limit": 25}
        )

    # ----------------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------------

    def _make_paginated_request(self, method: str, url_slug: str, **kwargs) -> list[dict[str, Any]]:
        params = kwargs.pop("params", {})
        records: list[dict[str, Any]] = []
        while True:
            resp = self._make_request(method, url_slug, params=params, **kwargs)
            records.extend(resp.get("records", []))
            next_token = resp.get("next_token")
            if next_token:
                params["nextToken"] = next_token
            else:
                break
        return records

    def _make_request(self, method: str, url_slug: str, **kwargs) -> dict[str, Any]:
        resp = self.session.request(method=method, url=f"{REQUEST_URL}/{url_slug}", **kwargs)
        resp.raise_for_status()
        return resp.json()

    def _format_dates(self, start_date: str | None, end_date: str | None) -> tuple[str, str]:
        end = datetime.combine(
            datetime.fromisoformat(end_date) if end_date else datetime.today(), time.max
        )
        start = datetime.combine(
            datetime.fromisoformat(start_date) if start_date else datetime.today() - timedelta(days=6),
            time.min,
        )
        if start > end:
            raise ValueError(f"Start datetime greater than end datetime: {start} > {end}")
        return (start.isoformat() + "Z", end.isoformat(timespec="seconds") + "Z")

    # ----------------------------------------------------------------------
    # PKCE HELPERS
    # ----------------------------------------------------------------------

    @staticmethod
    def _generate_code_verifier(length: int = 128) -> str:
        chars = string.ascii_letters + string.digits + "-._~"
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def _generate_code_challenge(code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
