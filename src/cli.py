"""The CLI entry point of the Zwergenland user manager."""


import json
from os import environ
from typing import Dict, List, Optional, TextIO
from click import argument, echo, group, option, File
from dotenv import dotenv_values

from authentication import authenticate
from excel_reader import ExcelReader, KindergardenExcelSheetConfiguration
from group import GroupHandler
from group_details import GroupDetails
from invitation import InvitationHandler
from user import UserHandler
from user_details import UserDetails


@group()
def cli():
    """Main entry point of the CLI argument parser."""
    echo("Zwergenland CLI")


@cli.command()
@argument('group_name')
@option('--email', help='The mail used for the group.')
@option('--collaboration-group', help='Shall for the group the collaboration features be enabled?')
def create_group(group_name: str, email: str | None, collaboration_group):
    """Create a new group if it is not already existing and return the UUID of the group.
       If the group is already existing, then the uuid of the existing group will be returned."""
    print(f"Command create group {group_name}...")
    env: Dict[str, str | None] = dict(environ) | dotenv_values()
    access_token = authenticate(env)

    email = email if email not in [None, ""] else group_name
    assert email is not None
    group_details = GroupDetails(group_name, email, True)

    group_handler = GroupHandler(access_token)
    group_details = group_handler.get_or_create(group_details)


@cli.command()
@argument('group_id', type=str)
@argument('user_file', type=File('r'))
def add_users(group_id: str, user_file: TextIO):
    """Add a user to an existing group."""
    echo(f"Adding users from {user_file.name} to group {group_id}")
    data = json.load(user_file)
    contacts = [UserDetails.from_dict(contact_dict) for contact_dict in data]

    env: Dict[str, str | None] = dict(environ) | dotenv_values()
    access_token = authenticate(env)
    group_handler = GroupHandler(access_token)
    invitation_handler = InvitationHandler(access_token)
    user_handler = UserHandler(access_token)
    existing_members = group_handler.get_group_members(group_id)
    existing_members = [item["id"] for item in existing_members]

    for user_details in contacts:
        print(user_details)
        user_data = user_handler.find_by_email(user_details.email)
        if user_data:
            print(f"  User {user_details.email} already existing.")
            user_id = user_data['id']
        else:
            if input(f"  User {user_details.email} does not exist. Create? (y/N)") == 'y':
                user_id = invitation_handler.send_invitation(user_details)
                user_handler.update_user(user_id, user_details)
            else:
                print("  Skipping...")

        if user_id is not None:
            if not user_id in existing_members:
                if input(f"  We need to add user {user_id} to group {group_id}. Continue? (y/N)") == 'y':
                    group_handler.add_user_to_group(group_id, user_id)

                else:
                    print("  Skipping...")
            else:
                print(f"  Skipping existing group member {user_details.email}.")
            user_id = None


@cli.command()
@argument('input_file', type=File('r'))
@option('--first-data-row', default=None, type=int, help="First row in the Excel sheet containing the data.")
def read_users(input_file: TextIO, first_data_row: Optional[int]):
    """Read user details from Excel."""
    input_file.close()
    echo(f"Reading from file {input_file.name} and the first data row {first_data_row}")

    excel_reader = ExcelReader(input_file.name)
    config = KindergardenExcelSheetConfiguration()
    # config = AssociationExcelSheetConfiguration()
    if first_data_row is not None:
        config.first_data_row = first_data_row

    contacts: List[UserDetails] = excel_reader.read_contacts(config)
    print("\nContacts:")
    for contact in contacts:
        print(contact)
    print("\nWriting as users.json")
    with open('users.json', 'w', encoding="utf-8") as file:
        json.dump([contact.to_dict() for contact in contacts], file, indent=2)


@cli.command()
@argument("user_id", type=str)
def delete_user(user_id: str):
    """Delete a user identified by its UUID."""
    env: Dict[str, str | None] = dict(environ) | dotenv_values()
    access_token = authenticate(env)

    user_handler = UserHandler(access_token)
    user_handler.delete_user_by_id(user_id)


@cli.command()
@argument("email", type=str)
def find_user(email: str):
    """Find user details of a user identified by email."""
    env: Dict[str, str | None] = dict(environ) | dotenv_values()
    access_token = authenticate(env)

    user_handler = UserHandler(access_token)
    user_handler.find_by_email(email)


@cli.command()
def cleanup_user_data():
    """Find all orphan guest users and offer to delete them."""
    env: Dict[str, str | None] = dict(environ) | dotenv_values()
    token = authenticate(env)

    user_handler = UserHandler(token)
    all_guests = user_handler.get_guests()
    guests_without_group = user_handler.filter_users_without_group(all_guests)
    for guest in guests_without_group:
        print(json.dumps(guest, indent=2))
        if input("User without any groups. Delete? (y/N)") == 'y':
            user_id = guest['id']
            user_handler.delete_user_by_id(user_id)


if __name__ == '__main__':
    cli()
