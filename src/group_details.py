"""Collect group details and generate Microsoft API JSON."""

from typing import Any, Dict


class GroupDetails:
    """Collect group details and generate Microsoft API JSON."""

    def __init__(self, name: str, email: str, collaboration_group: bool = False) -> None:
        self.name = name
        self._email = email
        self._collaboration_group = collaboration_group

    def get_group_dict(self) -> Dict[str, Any]:
        """Generate a dictionary to serialize for Microsoft 365 API."""

        group = {
            "displayName": self.name,
            "description": self.name,
            "mailEnabled": True,
            "mailNickname": self._email,
            "securityEnabled": False,
            "visibility": "Private"
        }

        if self._collaboration_group:
            group["groupTypes"] = ["Unified"]

        return group
