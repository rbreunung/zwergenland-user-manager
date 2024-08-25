"""Handle invitations API requests."""

import sys
import requests

from user_details import UserDetails

INVITATIONS_URL = "https://graph.microsoft.com/v1.0/invitations"


class InvitationHandler:  # [too-few-public-methods]
    """Handle invitations API requests."""

    def __init__(self, access_token: str):
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def send_invitation(self, user_details: UserDetails) -> str:
        """Send an invite to a user."""

        request_data = user_details.get_invite_dict("https://www.zwergenland-babelsberg.de", "KiTa Zwergenland")
        response = requests.post(INVITATIONS_URL, json=request_data, headers=self._headers, timeout=30)

        if response.status_code == 201:
            invitation_response = response.json()
            invited_user_id = invitation_response["invitedUser"]["id"]
            print(f"Einladung an {user_details.email} erfolgreich gesendet. Benutzer-ID: {invited_user_id}")
            return invited_user_id

        print(f"Fehler beim Senden der Einladung: {response.status_code}")
        print(response.json())
        sys.exit(1)
