"""This module holds the user details of a single user."""


from typing import Any, Dict


class UserDetails:
    """This class holds all user details."""

    def __init__(self, first_name: str, lastname: str, email: str, display_name: str | None = None):
        self._first_name = first_name
        self._lastname = lastname
        self.email = email

        if display_name is None:
            self._display_name = f"{first_name} {lastname}"
        else:
            self._display_name = display_name

    def get_user_details_dict(self) -> Dict[str, Any]:
        """Get a dictionary for serialization to Microsoft users graph API."""
        return {
            "givenName": self._first_name,
            "surname": self._lastname,
            "displayName": self._display_name,
            "mail": self.email
        }

    def get_invite_dict(self, landing_page: str, organization: str,
                        cc_receivers: Dict[str, str] | None = None) -> Dict[str, Any]:
        """Get a dictionary for serialization to Microsoft invitations graph API.

        Args:
            landing_page (str): The landing page after the invite is accepted.
            cc_receivers (Dict[str,str]): Optional CC recipients of the invitation.

        Returns:
            Dict[str, Any]: Content ready to serialize.
        """
        cc_recipient_list = [{"emailAddress": {"name": name, "address": address}}
                             for name, address in cc_receivers.items()] if cc_receivers else []
        message = f"Hallo {self._display_name}, willkommen im Email-Verteiler von {organization}!"

        invite = {
            "invitedUserEmailAddress": self.email,
            "inviteRedirectUrl": landing_page,
            "sendInvitationMessage": False,
            "invitedUserDisplayName": self._display_name,
            "invitedUserMessageInfo": {
                "customizedMessageBody": message,
                "ccRecipients": cc_recipient_list
            }
        }

        return invite
