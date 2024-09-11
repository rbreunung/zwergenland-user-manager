"""Contains class ExcelReader and default behavior constants."""
from typing import List
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

    def read_contacts(self, config: KindergardenExcelSheetConfiguration | AssociationExcelSheetConfiguration) -> List[UserDetails]:  # pylint: disable=C0301
        """Read the Excel file in the child-parent-format and parse parent contacts."""
        print("\nhello\n")

        sheet = self._get_sheet(config)
        assert isinstance(config.first_data_row, int), "First data row is expected to be set here."
        contacts = []
        last_name_1_column_index = self._excel_col_to_index(config.last_name_1_column)

        for index in range(config.first_data_row, len(sheet)):
            cell_value = sheet.iloc[index, last_name_1_column_index]
            if pandas.isna(cell_value):
                print(f"Stopping iteration at index {index} where Column {last_name_1_column_index} is empty")
                break
            print(f"{cell_value} ")
        return contacts
