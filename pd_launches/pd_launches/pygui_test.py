import PySimpleGUI as sg
import tomli

with open("pd_launches.toml", "rb") as f:
    data = tomli.load(f)

CSV = data["csv_file"]
PD_LAUNCHES_SHEET = data["PD_LAUNCHES"]["smartsheet_name"]
PD_LAUNCHES_SS_COLS = "\n".join(data["PD_LAUNCHES"]["smartsheet_columns"])
HOLDS_SHEET = data["HOLDS"]["smartsheet_name"]
HOLDS_COLUMNS = "\n".join(data["HOLDS"]["smartsheet_columns"])
RENAME_NS_COLUMNS = data["RENAME_NS_COLUMNS"]
DATEFIELDS = data["DATEFIELDS"]["columns"]

# sg.theme_previewer()

sg.theme("BrightColors")  # Add some color to the window

# Very basic window.  Return values using auto numbered keys

text_size = (25, 1)
input_size = (45, 20)
layout = [
    [sg.Text("Please enter PD Launches variables.\n")],
    [
        sg.Text("CSV Filepath", size=text_size),
        sg.InputText(CSV, background_color="pink"),
    ],
    [
        sg.Text("PD Launches Smartsheet Name", size=text_size),
        sg.InputText(PD_LAUNCHES_SHEET, background_color="pink"),
    ],
    [
        sg.Text("PD Launches SS Columns", size=text_size),
        sg.Multiline(PD_LAUNCHES_SS_COLS, s=input_size, background_color="pink"),
    ],
    [
        sg.Text("Holds Smartsheet Name", size=text_size),
        sg.InputText(HOLDS_SHEET, background_color="pink"),
    ],
    [
        sg.Text("Holds SS Columns", size=text_size),
        sg.Multiline(HOLDS_COLUMNS, s=input_size, background_color="pink"),
    ],
    [sg.Submit(), sg.Cancel()],
]

window = sg.Window("PD Launches", layout)
event, values = window.read()
window.close()
# print(event, values[0], values[1], values[2])    # the input data looks like a simple list when auto numbered
# for i in values:
#     print(i)

print(values[4])

a = values[4].split("\n")

print(a)
