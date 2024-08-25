"""Handle groups API requests."""


import json
import sys
from typing import Any, Dict, List
import requests

from group_details import GroupDetails


GROUPS_URL = "https://graph.microsoft.com/v1.0/groups"


class GroupHandler:   # [too-few-public-methods]
    """Handle groups API requests."""

    def __init__(self, access_token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

    def get_all_groups(self) -> List[Any] | None:
        """Get all groups defined in the organization."""
        response = requests.get(GROUPS_URL, headers=self._headers, timeout=30)
        groups = response.json()
        assert isinstance(groups, dict)
        print(json.dumps(groups, indent=2))
        return groups.get("value", None)

    def create_group(self, group_details: GroupDetails) -> Dict | None:
        """Create a Microsoft 365 Group."""
        response = requests.post(GROUPS_URL, headers=self._headers, json=group_details.get_group_dict(), timeout=30)
        assert response.status_code == 201
        print("--- creating group ---")
        print(json.dumps(response.json(), indent=2))
        print("---")
        return response.json().get('value', None)

    def get_group(self, group_name: str) -> Dict | None:
        """Get a Microsoft 365 group by the starting letters of the Name."""
        params = {
            "$filter": f"startswith(displayName, '{group_name}')"  # 'contains' is not supported.
        }

        response = requests.get(GROUPS_URL, headers=self._headers, params=params, timeout=30)

        # Check the response status and print the results
        if response.status_code == 200:
            groups = response.json().get('value', None)
            if groups:
                if len(groups) > 1:
                    print(f"--- {len(groups)} group(s) found. Taking following ---")
                else:
                    print("--- found group ---")
                for group in groups:
                    print(json.dumps(group, indent=2))
                    print("---")
                    return group
            else:
                print(f"No group found starting with '{group_name}'.")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            sys.exit(1)
        return None

    def get_or_create(self, group: GroupDetails) -> Dict | None:
        """Try to find an existing group with the specified name.
        If it is not found, then it will be created with the given details."""
        found_group = self.get_group(group.name)

        if found_group:
            return found_group

        return self.create_group(group)

    def add_user_to_group(self, group_id: str, user_id: str) -> bool:
        """Generic add a user to a group.

        Args:
            group_id (str): The group UUID
            user_id (str): The user UUID

        Returns:
            bool: True only if the user is successfully and newly added. False if already in group or other issues.
        """

        url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"
        data = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"
        }
        response = requests.post(url, headers=self._headers, json=data, timeout=30)

        if response.status_code == 204:
            print(f"User {user_id} added to group {group_id} successfully.")
            return True

        print(f"Error: {response.status_code} User {user_id} and group {group_id}")
        print(response.json())
        return False

    def get_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """Get all members of the group"""
        url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members"
        response = requests.get(url, headers=self._headers, timeout=30)

        if response.status_code == 200:  # 200 OK means success
            members = response.json().get('value', [])
            print(f"--- Mitglieder von {group_id} ---")
            for member in members:
                print(json.dumps(member, indent=2))
                print("---")
            print("--- ---")
            return members

        print(f"Error: {response.status_code}")
        print(response.json())
        sys.exit(1)
