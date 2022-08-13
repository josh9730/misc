import keyring
import pandas as pd
import smartsheet

NS_CSV_DUMP = "NewPDPhotographyNeeded8-7.csv"
PD_LAUNCHES_SHEET_NAME = "New PD Launches (NOT LIVE)"
HOLDS_SHEET = "ROs and Holds (NOT LIVE)"
SS_COLUMNS = [
    "Item",  # renamed from 'Name' in csv
    "Description",
    "Anticipated Launch Date",
    "Launch Notes",
    "eCommerce Notes",
    "Earliest PO/WO Date",
    "Photo Notes",
    "Photograph",
    "Date Photo Completed?",
    "Design Approval Date",
    "Design Approval Status",
    "How Produced",
]
SS_COLUMNS.sort()


def check_csv_columns(df: pd.DataFrame) -> None:
    """Check that SS_COLUMNS exist in DF as imported from csv."""
    df_col_list = list(df.columns)
    for col in SS_COLUMNS:
        if col not in df_col_list:
            raise ValueError(f"{col} not present in CSV import.")


def get_sheet_id(ss_client: smartsheet, sheet_name: str) -> int:
    """Return Sheet ID from Sheet Name."""
    sheet_dict = ss_client.Sheets.list_sheets(include_all=True).to_dict()
    for sheet in sheet_dict["data"]:
        if sheet["name"].upper() == sheet_name.upper():
            return sheet["id"]
    raise NameError("Cannot find the specified Smartsheet")


def import_csv_df() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Import and drop unneeded columns from CSV, creates appropriately formatted DFs.

    For Anticipated Launch Date, if any cells are not datetime, then the rows are moved to a Hold sheet.
    """

    def convert_date(date: str) -> str:
        """Specifically for Anticipated..., used to convert to isoformat.

        Returns isoformatted string, unmodified date arg, or '202'. '202'
        is specifically to 'mark' empty fields to be grouped with rows with valid datetimes for
        uploading to the non-Hold sheet. In other words, the rows that get sent to the non-Hold sheet start with '202'.

        Fields that match '202' are returned to blanks after creating the non-Hold DF.
        """
        if date:
            if "/" in date:
                # coerce to isoformat
                month, day, year = date.split("/")
                return f'{year}-{month.rjust(2, "0")}-{day.rjust(2, "0")}'
            else:
                return date
        return "202"  # used to return back to blank after hold_df removed, as in first 2 characters of datetime

    df = pd.read_csv(NS_CSV_DUMP).fillna("")
    df.rename(
        columns={"Name": "Item", "Date Photo Completed": "Date Photo Completed?"},
        inplace=True,
    )

    check_csv_columns(df)

    for date_field in (
        "Earliest PO/WO Date",
        "Design Approval Date",
        "Date Photo Completed?",
    ):
        df[date_field] = pd.to_datetime(
            df[date_field], errors="coerce", infer_datetime_format=True
        )
        df[date_field] = df[date_field].astype(str).replace({"NaT": ""})

    # convert and add to new column
    df["Anticipated Launch Date"] = df["Anticipated Launch Date"].apply(
        lambda x: convert_date(x)
    )

    # pull out rows that do not start with a '202', ie a date
    hold_df = df[~df["Anticipated Launch Date"].str.startswith("202")]

    # filter for rows with '202' and return '202' back to blank
    df = df[df["Anticipated Launch Date"].str.startswith("202")]
    df["Anticipated Launch Date"].replace("202", "", inplace=True)

    hold_df = hold_df[
        [
            "Item",
            "Description",
            "Photograph",
            "Anticipated Launch Date",
        ]
    ]

    return df[SS_COLUMNS], hold_df


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
    ss_client: smartsheet,
    sheet: smartsheet.models.Sheet,
    new_df: pd.DataFrame,
    ignore_col_err: bool = False,
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
                sheet_col = sheet.get_column_by_title(col_name)
                if sheet_col:
                    new_row.cells.append(
                        {
                            "column_id": sheet_col.id,
                            "value": row[col_name],
                        }
                    )
                else:
                    if ignore_col_err:
                        pass
                    else:
                        raise IndexError(f"{col_name} does not exist on sheet.")
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
    sheet_id = get_sheet_id(ss_client, PD_LAUNCHES_SHEET_NAME)
    hold_sheet_id = get_sheet_id(ss_client, HOLDS_SHEET)
    pd_sheet = ss_client.Sheets.get_sheet(sheet_id)
    hold_sheet = ss_client.Sheets.get_sheet(hold_sheet_id)
    active_items = get_active_items(pd_sheet)
    hold_active_items = get_active_items(hold_sheet)

    csv_df, hold_df = import_csv_df()

    # remove rows already present on SS
    new_df = csv_df[~csv_df["Item"].isin(active_items)].reset_index()
    new_hold_df = hold_df[~hold_df["Item"].isin(hold_active_items)].reset_index()

    upload_new_df(ss_client, pd_sheet, new_df)
    upload_new_df(ss_client, hold_sheet, new_hold_df)


if __name__ == "__main__":
    main()
