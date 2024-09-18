"""Contains class ExcelReader and default behavior constants."""
from typing import List, Optional
import pandas

from user_details import UserDetails

# all row constants are 0 based, while Excel UI is 1 based


class AssociationExcelSheetConfiguration:  # pylint: disable=R0903
    """Association Configuration Model"""
    sheet_id: str | int | None = None
    first_data_row: int | None = None
    last_name_1_headline = 'name1'
    # Mutter
    first_name_1_column: str = 'B'
    last_name_1_column: str = 'A'
    email_1_column: str = 'J'
    phone_1_column: str | None = None
    # Vater
    first_name_2_column: str = 'D'
    last_name_2_column: str = 'C'
    email_2_column: str = 'K'
    phone_2_column: str | None = None
    # Kind
    child_name: str | None = None


class KindergardenExcelSheetConfiguration:  # pylint: disable=R0903
    """Kindergarden Configuration Model"""
    sheet_id: str | int | None = None
    first_data_row: int | None = None
    last_name_1_headline = 'namem'
    # Mutter
    first_name_1_column: str = 'X'
    last_name_1_column: str = 'W'
    email_1_column: str = 'AM'
    phone_1_column: str | None = 'AK'
    # Vater
    first_name_2_column: str = 'Z'
    last_name_2_column: str = 'Y'
    email_2_column: str = 'AN'
    phone_2_column: str | None = 'AL'
    # Kind
    child_name: str | None = 'C'


class ExcelReader:
    """The behavior necessary to open a .xlsx file and parse the contacts from the known format."""

    def __init__(self, file_name: str) -> None:
        self._file: pandas.ExcelFile = pandas.ExcelFile(file_name, engine='openpyxl')

    def _excel_col_to_index(self, col: str) -> int:
        index: int = 0
        for char in col:
            index = index * 26 + (ord(char.upper()) - ord('A') + 1)
        return index - 1

    def _get_sheet(self, config: KindergardenExcelSheetConfiguration | AssociationExcelSheetConfiguration) -> pandas.DataFrame:  # pylint: disable=C0301
        """Validate / Complete the configuration and get the sheet."""
        if config.sheet_id is None:
            config.sheet_id = self._file.sheet_names[0]
        data_frame = self._file.parse(config.sheet_id, header=None)
        assert data_frame is not None, "sheet should be available here."

        if config.first_data_row is None:
            column_index = self._excel_col_to_index(config.last_name_1_column)
            # Iterate over the DataFrame to find the first row where column matches known headline.
            for i in range(len(data_frame)):
                value = data_frame.iat[i, column_index]
                if value == config.last_name_1_headline:
                    print(f"First row where column {column_index+1} matches expected headline is: {i+1}")
                    config.first_data_row = i + 1
                    break

        assert config.first_data_row is not None, "Expected headline not found in sheet."

        return data_frame

    def _check_and_add_user_details(self, first_name, lastname, email, contacts: List[UserDetails], index: int):
        """Check the input values whether they are feasible to create a user detail to import as a mail contact. Add user if feasible. Else log."""
        if not pandas.isna(email):
            print(f"{email} ")
            contacts.append(UserDetails(str(first_name), str(lastname), str(email)))
            return

        print(f"User details in line {index} skipped.")
        return None

    def read_contacts(self, config: KindergardenExcelSheetConfiguration | AssociationExcelSheetConfiguration) -> List[UserDetails]:  # pylint: disable=C0301
        """Read the Excel file in the child-parent-format and parse parent contacts."""
        print("\nhello\n")

        sheet = self._get_sheet(config)
        assert isinstance(config.first_data_row, int), "First data row is expected to be set here."
        last_name_1_column_index = self._excel_col_to_index(config.last_name_1_column)
        first_name_1_column_index = self._excel_col_to_index(config.first_name_1_column)
        email_1_column_index = self._excel_col_to_index(config.email_1_column)
        last_name_2_column_index = self._excel_col_to_index(config.last_name_2_column)
        first_name_2_column_index = self._excel_col_to_index(config.first_name_2_column)
        email_2_column_index = self._excel_col_to_index(config.email_2_column)

        contacts: List[UserDetails] = []
        for index in range(config.first_data_row, len(sheet)):
            last_name_1 = sheet.iloc[index, last_name_1_column_index]
            first_name_1 = sheet.iloc[index, first_name_1_column_index]
            email_1 = sheet.iloc[index, email_1_column_index]
            last_name_2 = sheet.iloc[index, last_name_2_column_index]
            first_name_2 = sheet.iloc[index, first_name_2_column_index]
            email_2 = sheet.iloc[index, email_2_column_index]

            if pandas.isna(email_1) and pandas.isna(email_2):
                print(f"Stopping iteration at index {index} where email Column {email_1_column_index} and {email_2_column_index} are empty.")
                break

            self._check_and_add_user_details(first_name_1, last_name_1, email_1, contacts, index)
            self._check_and_add_user_details(first_name_2, last_name_2, email_2, contacts, index)

        return contacts
