"""The CLI entry point of the Zwergenland user manager."""


from typing import Optional, TextIO
from click import argument, echo, group, option, File

from excel_reader import ExcelReader, KindergardenExcelSheetConfiguration


@group()
def cli():
    """Main entry point of the CLI argument parser."""
    echo("Zwergenland CLI")


@cli.command()
def create_group():
    """Create a new group if it is not already existing."""
    print("Hello Group")


@cli.command()
@argument('group_id')
@argument('user_id')
def add_user(group_id: str, user_id: str):
    """Add a user to an existing group."""
    echo(f"Adding user {user_id} to group {group_id}")


@cli.command()
@argument('input_file', type=File('r'))
@option('--first-data-row', default=3, type=int, help="First row in the Excel sheet containing the data.")
def read_users(input_file: TextIO, first_data_row: Optional[int]):
    """Read user details from Excel."""
    input_file.close()
    echo(f"Reading from file {input_file.name} and the first data row {first_data_row}")
    excel_reader = ExcelReader(input_file.name)
    config = KindergardenExcelSheetConfiguration()
    excel_reader.read_contacts(config)


if __name__ == '__main__':
    cli()
