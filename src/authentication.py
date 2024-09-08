"""Handle the Authentication with Microsoft 365 OAUTH."""
from typing import Dict
import requests


# Get an access token


def authenticate(env: Dict[str, str | None]) -> str:
    """Authenticate with Microsoft 365 and provide an authentication token used with other APIs."""

    client_id = env['CLIENT_ID']
    client_secret = env['CLIENT_SECRET']
    tenant_id = env['TENANT_ID']
    grant_type = 'client_credentials'
    access_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": grant_type
    }

    response = requests.post(access_url, headers=headers, data=data, timeout=30)
    token_response = response.json()
    access_token = token_response.get('access_token')
    return access_token
