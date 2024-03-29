import keyring
import pandas as pd
import smartsheet


class PDLaunchUpload:
    def __init__(self, data: dict) -> None:

        self.pd_launch_sheet_name = data["pd_launches"]["smartsheet_name"]
        self.holds_sheet_name = data["holds"]["smartsheet_name"]
        self.pd_ss_columns = data["pd_launches"]["smartsheet_columns"]
        self.pd_ss_columns.sort()
        self.hold_ss_columns = data["holds"]["smartsheet_columns"]

        self.csv_file = data["csv_file"]
        self.column_rename = data["rename_ns_columns"]
        self.date_columns = data["date_columns"]

        self.ss_client = self._open_smartsheets()
        pd_launch_sheet_id = self._get_sheet_id(self.pd_launch_sheet_name)
        holds_sheet_id = self._get_sheet_id(self.holds_sheet_name)

        self.pd_launch_ss = self.ss_client.Sheets.get_sheet(pd_launch_sheet_id)
        self.holds_ss = self.ss_client.Sheets.get_sheet(holds_sheet_id)

        self.pd_active_items = self._get_active_items(self.pd_launch_ss)
        self.holds_active_items = self._get_active_items(self.holds_ss)

    def _open_smartsheets(self) -> smartsheet:
        """Initialize Smartsheets object."""
        access_token = keyring.get_password("rings_smartsheets", "api")
        ss_client = smartsheet.Smartsheet(access_token)
        ss_client.errors_as_exceptions(True)
        return ss_client

    def _get_sheet_id(self, sheet_name: str) -> int:
        """Return Sheet ID from Sheet Name."""
        sheet_dict = self.ss_client.Sheets.list_sheets(include_all=True).to_dict()
        for sheet in sheet_dict["data"]:
            if sheet["name"].upper() == sheet_name.upper():
                return sheet["id"]
        raise NameError("Cannot find the specified Smartsheet")

    def _get_active_items(self, sheet: smartsheet.models.Sheet) -> list:
        """Return list of values from Item column. Used to filter incoming csv."""
        return [
            cell.value
            for row in sheet.rows
            for cell in row.cells
            if cell.column_id == sheet.get_column_by_title("Item").id
        ]

    def _check_csv_columns(self, df: pd.DataFrame) -> None:
        """Check that SS_COLUMNS exist in DF as imported from csv.
        Must be called after renaming the appropriate columns.
        """
        df_col_list = list(df.columns)
        for col in self.pd_ss_columns:
            if col not in df_col_list:
                raise ValueError(f"{col} not present in CSV import.")

    def create_dfs_from_csv(self) -> None:
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
                    if len(year) == 2:
                        year = "20" + year
                    return f'{year}-{month.rjust(2, "0")}-{day.rjust(2, "0")}'
                else:
                    return date
            return "202"  # used to return back to blank after hold_df removed, as in first 2 characters of datetime

        pd_df = pd.read_csv(self.csv_file).fillna("")
        pd_df.rename(columns=self.column_rename, inplace=True)

        self._check_csv_columns(pd_df)

        # drop rows with Items starting with 'BE1' amd ending with 'LC'
        pd_df.drop(pd_df.index[pd_df["Item"].str.match("^BE1.*LC$")], inplace=True)

        for date_field in (
            "Earliest PO/WO Date",
            "Design Approval Date",
            "Date Photo Completed?",
        ):
            pd_df[date_field] = pd.to_datetime(
                pd_df[date_field], errors="coerce", infer_datetime_format=True
            )
            pd_df[date_field] = pd_df[date_field].astype(str).replace({"NaT": ""})

        # convert and add to new column
        pd_df["Anticipated Launch Date"] = pd_df["Anticipated Launch Date"].apply(
            lambda x: convert_date(x)
        )

        # pull out rows that do not start with a '202', ie a date
        hold_df = pd_df[~pd_df["Anticipated Launch Date"].str.startswith("202")]

        # if Description startswith 'runout' move to holds
        runouts = pd_df[pd_df['Description'].str.match('runout.*', case=False)]
        hold_df = pd.concat([hold_df, runouts])

        # filter for rows with '202' and return '202' back to blank
        pd_df = pd_df[pd_df["Anticipated Launch Date"].str.startswith("202")]
        pd_df["Anticipated Launch Date"].replace("202", "", inplace=True)

        # remove rows already present on SS
        self.pd_df = pd_df[~pd_df["Item"].isin(self.pd_active_items)].reset_index()
        self.hold_df = hold_df[
            ~hold_df["Item"].isin(self.holds_active_items)
        ].reset_index()

    def return_uploads(self) -> tuple[list, list]:
        """Print the Items that will be uploaded to the PD Launches and Holds smartsheets."""
        pd_items, hold_items = [], []
        if not self.pd_df["Item"].empty:
            pd_items = self.pd_df["Item"].tolist()
        if not self.hold_df["Item"].empty:
            hold_items = self.hold_df["Item"].tolist()

        return pd_items, hold_items

    def upload_dfs(self) -> None:
        """Iterates over csv dataframe and uploads to Smartsheets.

        Adds one new Row at a time. Attemping to add a list of Rows gives error:
            'Invalid row location: You must use at least 1 location specifier'
        even though toBottom is set.

        overrideValidation is set to True to allow for PickLists. Via API non-required conformity
        seems to be required.
        """

        def _create_and_upload(
            sheet: smartsheet.models.Sheet, df: pd.DataFrame, ss_columns: list[str]
        ):
            """Helper function to perform the DF upload to Smartsheets."""
            if not df.empty:
                for index, row in df.iterrows():
                    new_row = self.ss_client.models.Row()
                    for col_name in ss_columns:
                        if row.get(col_name):  # can't append cells with empty values
                            sheet_col = sheet.get_column_by_title(col_name)
                            if sheet_col:
                                new_row.cells.append(
                                    {
                                        "column_id": sheet_col.id,
                                        "value": row[col_name],
                                        "overrideValidation": True,
                                        "strict": False,
                                    }
                                )
                            else:
                                raise IndexError(f"{col_name} does not exist on sheet.")
                    new_row.toBottom = True
                    sheet.add_rows(new_row)

        _create_and_upload(self.pd_launch_ss, self.pd_df, self.pd_ss_columns)
        _create_and_upload(self.holds_ss, self.hold_df, self.hold_ss_columns)
