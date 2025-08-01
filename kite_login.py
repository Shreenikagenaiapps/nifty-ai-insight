from kiteconnect import KiteConnect
from typing import Any, Dict
import os
import json
import datetime

# Load credentials from environment
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")
access_token_file = "access_token.json"

# Create KiteConnect instance
kite = KiteConnect(api_key=api_key)

def get_login_url() -> str:
    """
    Returns the URL where the user should log in to get the request token.
    """
    return kite.login_url()

def generate_session(request_token: str) -> str | None:
    """
    Uses the request token to generate access token and saves it (JSON-serializable only).
    """
    try:
        raw_response: Any = kite.generate_session(
            request_token=request_token,
            api_secret=api_secret
        )

        # Ensure it's a dict
        if not isinstance(raw_response, dict):
            raise TypeError("Expected response to be a dictionary")

        # Convert datetime fields to strings
        session_data: Dict[str, Any] = {
            key: (value.isoformat() if isinstance(value, datetime.datetime) else value)
            for key, value in raw_response.items()
        }

        access_token = session_data["access_token"]
        kite.set_access_token(access_token)

        # Save to file
        with open(access_token_file, "w") as f:
            json.dump(session_data, f)

        print("✅ Access token saved to file.")
        return access_token

    except Exception as e:
        print(f"❌ Failed to generate session: {e}")
        return None

def load_access_token() -> str | None:
    """
    Loads access token from file and sets it in Kite client.
    """
    if not os.path.exists(access_token_file):
        print("⚠️ Access token file not found.")
        return None

    try:
        with open(access_token_file, "r") as f:
            session_data = json.load(f)

        access_token = session_data["access_token"]
        kite.set_access_token(access_token)
        return access_token

    except Exception as e:
        print(f"❌ Failed to load access token: {e}")
        return None
