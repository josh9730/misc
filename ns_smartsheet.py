# Note: Smartsheet library does not work with python3.10
from datetime import datetime

import keyring
import pandas as pd
import smartsheet

NS_CSV_DUMP = "NewPDPhotographyNeededROCResults930.csv"
PD_LAUNCHES_SHEET_NAME = "New PD Launches"
SS_COLUMNS = [
    "Item",  # renamed from 'Name' in csv
    "Description",
    "Anticipated Launch Date",
    "Launch Notes",
    "eCommerce Notes",
    "Earliest PO/WO Date",
    "Photo Notes",
    "Photograph",
    "Copy Complete?",  # renamed from 'Notes for Copy' in csv
    "Date Photo Completed",
    "Design Approval Date",
    "Design Approval Status",
]


def get_sheet_id(ss_client: smartsheet) -> int:
    """Return Sheet ID from Sheet Name."""
    sheet_dict = ss_client.Sheets.list_sheets(include_all=True).to_dict()
    for sheet in sheet_dict["data"]:
        if sheet["name"] == PD_LAUNCHES_SHEET_NAME:
            return sheet["id"]


def import_csv_df() -> pd.DataFrame:
    """Import and drop unneeded columns."""

    def convert_date(date):
        """Smartsheets requires isoformatted dates. Non-dates are converted to blank strings."""
        if date:
            if "/" in date:  # coerce to isoformat
                month, day, year = date.split("/")
                return f'{year}-{month.rjust(2, "0")}-{day.rjust(2, "0")}'
            else:
                try:
                    datetime.fromisoformat(date)
                except ValueError:  # handle non-date fields
                    print(
                        f"Value: {date} is an invalid date, converted to empty string."
                    )
                    return ""

    df = pd.read_csv(NS_CSV_DUMP).fillna("")
    df.rename(
        columns={"Name": "Item", "Notes for Copy": "Copy Complete?"}, inplace=True
    )

    for date_field in (
        "Anticipated Launch Date",
        "Earliest PO/WO Date",
        "Design Approval Date",
        "Date Photo Completed",
    ):
        df[date_field] = df[date_field].apply(lambda x: convert_date(x))

    return df[[*SS_COLUMNS]]


def open_smartsheets() -> smartsheet:
    """Initialize Smartsheets object."""
    access_token = keyring.get_password("rings_smartsheets", "api")
    ss_client = smartsheet.Smartsheet(access_token)
    ss_client.errors_as_exceptions(True)
    return ss_client


def get_active_items(sheet: smartsheet.models.Sheet) -> list:
    """Return list of values from Item column. Used to filter incoming csv."""
    return [
        cell.value
        for row in sheet.rows
        for cell in row.cells
        if cell.column_id == sheet.get_column_by_title("Item").id
    ]


def upload_new_df(
    ss_client: smartsheet, sheet: smartsheet.models.Sheet, new_df: pd.DataFrame
) -> None:
    """Iterates over csv dataframe and uploads to Smartsheets.

    Adds one new Row at a time. Attemping to add a list of Rows gives error:
        'Invalid row location: You must use at least 1 location specifier'
    even though toBottom is set.
    """
    for index, row in new_df.iterrows():
        new_row = ss_client.models.Row()
        for col_name in SS_COLUMNS:
            if row[col_name]:  # can't append cells with empty values
                new_row.cells.append(
                    {
                        "column_id": sheet.get_column_by_title(col_name).id,
                        "value": row[col_name],
                    }
                )
        new_row.toBottom = True
        sheet.add_rows(new_row)


def main():
    """Uploads new items from CSV to Smartsheets.

    - Open Smartsheets API
    - Return unique Sheet ID field based on name constant
    - Open Sheet and return list of all Items
    - create DataFrame from Netsuite CSV
    - Prune items that exist in the Smartsheets Item list from the Dataframe
    - Upload remaining 'new' items from DataFrame to Smartsheets
    """
    ss_client = open_smartsheets()
    sheet_id = get_sheet_id(ss_client)
    pd_sheet = ss_client.Sheets.get_sheet(sheet_id)
    active_items = get_active_items(pd_sheet)

    csv_df = import_csv_df()

    new_df = csv_df[~csv_df["Item"].isin(active_items)].reset_index()
    upload_new_df(ss_client, pd_sheet, new_df)


if __name__ == "__main__":
    main()
