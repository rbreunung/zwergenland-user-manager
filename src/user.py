"""Handle users API requests."""

import json
import sys
from typing import Any, Dict
import requests
from user_details import UserDetails

USERS_URL = "https://graph.microsoft.com/v1.0/users"


class UserHandler:
    """Handle users API requests."""

    def __init__(self, access_token: str):
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def update_user(self, user_id: str, user_details: UserDetails | Dict[str, Any]) -> Dict[str, Any] | None:
        """Update user details of the user with given ID.

        Args:
            user_id (str): UUID of the user.
            user_details (UserDetails | Dict[str, Any]): Either the user details object or
                a data structure as expected by Microsoft 365 API.

        Returns:
            Dict[str, Any] | None: 
        """
        update_user_url = f"{USERS_URL}/{user_id}"

        if isinstance(user_details, UserDetails):
            update_data = user_details.get_user_details_dict()
        else:
            update_data = user_details

        response = requests.patch(update_user_url, json=update_data, headers=self._headers, timeout=30)

        if response.status_code == 204:
            print(f"Benutzerinformationen für {update_data['mail']} wurden erfolgreich aktualisiert.")
            return self.get_by_id(user_id)

        print(f"Fehler beim Aktualisieren der Benutzerinformationen: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        sys.exit(1)

    def get_guests(self):
        """Get all users of type guest."""
        params = {
            "$filter": "userType eq 'Guest'"
        }

        response = requests.get(USERS_URL, headers=self._headers, params=params, timeout=30)

        if response.status_code == 200:
            guests = response.json().get('value', [])
            print(f"\n\nEs wurden {len(guests)} Gastbenutzer gefunden:\n")
            for guest in guests:
                print(json.dumps(guest, indent=2))
            return guests
        print(f"Fehler beim Abrufen der Gastbenutzer: {response.status_code}")
        print(response.json())
        sys.exit(1)

    def find_by_email(self, email: str) -> Dict[str, Any] | None:
        """Find user by 'mail' attribute."""
        params = {
            "$filter": f"mail eq '{email}'"
        }

        response = requests.get(USERS_URL, headers=self._headers, params=params, timeout=30)

        if response.status_code == 200:
            users = response.json().get('value', None)
            if users:
                print("-- user found ---")
                for user in users:
                    print(json.dumps(user, indent=2))
                    print("---")
                    return user
            else:
                print("No user found with that email address.")
        else:
            print(f"Error: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            sys.exit(1)
        return None

    def get_by_id(self, user_id: str) -> Dict[str, Any] | None:
        """Get a user by UUID from Microsoft 365 directory."""
        get_user_url = f"{USERS_URL}/{user_id}"
        response = requests.get(get_user_url, headers=self._headers, timeout=30)

        if response.status_code == 200:
            user = response.json()
            print("-- user found ---")
            print(json.dumps(user, indent=2))
            print("---")
            return user

        print(f"Error Code {response.status_code} while trying to find user id '{user_id}'.")
        print(json.dumps(response.json(), indent=2))
        return None
