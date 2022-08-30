import PySimpleGUI as sg


class PDGUI:

    sg.theme("BrightColors")

    def __init__(self, data: dict) -> None:
        self.CSV = data["csv_file"]
        self.PD_LAUNCHES_SHEET = data["pd_launches"]["smartsheet_name"]
        self.PD_LAUNCHES_SS_COLS = "\n".join(data["pd_launches"]["smartsheet_columns"])
        self.HOLDS_SHEET = data["holds"]["smartsheet_name"]
        self.HOLDS_COLUMNS = "\n".join(data["holds"]["smartsheet_columns"])
        self.RENAME_NS_COLUMNS = data["rename_ns_columns"]
        self.DATEFIELDS = data["date_columns"]

    def create_gui(self) -> str:

        # sg.theme("BrightColors")
        text_size = (25, 1)
        input_size = (45, 20)
        layout = [
            [sg.Text("Please enter PD Launches variables.\n")],
            [
                sg.Text("CSV Filepath", size=text_size),
                sg.InputText(self.CSV, background_color="pink", key="-CSV-"),
            ],
            [
                sg.Text("PD Launches Smartsheet Name", size=text_size),
                sg.InputText(
                    self.PD_LAUNCHES_SHEET, background_color="pink", key="-PD_SHEET-"
                ),
            ],
            [
                sg.Text("PD Launches SS Columns", size=text_size),
                sg.Multiline(
                    self.PD_LAUNCHES_SS_COLS,
                    s=input_size,
                    background_color="pink",
                    key="-PD_COLS-",
                ),
            ],
            [
                sg.Text("Holds Smartsheet Name", size=text_size),
                sg.InputText(
                    self.HOLDS_SHEET, background_color="pink", key="-HOLD_SHEET-"
                ),
            ],
            [
                sg.Text("Holds SS Columns", size=text_size),
                sg.Multiline(
                    self.HOLDS_COLUMNS,
                    s=input_size,
                    background_color="pink",
                    key="-HOLD_COLS-",
                ),
            ],
            [sg.Submit(), sg.Cancel()],
        ]

        window = sg.Window("PD Launches", layout, finalize=True)
        event, self.values = window.read()
        window.close()
        return event

    def return_dict_values(self) -> dict:
        return {
            "csv_file": self.values["-CSV-"],
            "pd_launches": {
                "smartsheet_name": self.values["-PD_SHEET-"],
                "smartsheet_columns": self.values["-PD_COLS-"].split("\n"),
            },
            "holds": {
                "smartsheet_name": self.values["-HOLD_SHEET-"],
                "smartsheet_columns": self.values["-HOLD_COLS-"].split("\n"),
            },
            "date_columns": self.DATEFIELDS,
            "rename_ns_columns": self.RENAME_NS_COLUMNS,
        }

    def confirmation_gui(self, pd_items: list[str], hold_items: list[str]) -> None:
        text_size = (25, 1)
        input_size = (45, 20)
        layout = [
            [
                sg.Text(
                    "The following Items will be uploaded to Smartsheets upon confirmation:"
                )
            ],
            [
                sg.Text("PD Launches Items", size=text_size),
                sg.Multiline(
                    "\n".join(pd_items),
                    s=input_size,
                    disabled=True,
                    background_color="pink",
                ),
            ],
            [
                sg.Text("Hold Items", size=text_size),
                sg.Multiline(
                    "\n".join(hold_items),
                    s=input_size,
                    disabled=True,
                    background_color="pink",
                ),
            ],
            [sg.Submit(), sg.Cancel()],
        ]

        window = sg.Window("Upload Confirmation", layout, finalize=True)
        event, values = window.read()
        window.close()
        return event

    def final_window(self):
        text_size = (25, 1)
        layout = [
            [sg.Text("Program completed!", size=text_size)],
            [sg.Ok()],
        ]
        window = sg.Window("Program Completed", layout, finalize=True)
        event, values = window.read()
        window.close()
