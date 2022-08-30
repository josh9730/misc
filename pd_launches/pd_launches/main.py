import argparse
import json
import sys

import pd
import pd_gui

"""
- how to handle picklist?

"""


INPUT_FILE = "data.json"


def main(args):
    with open(INPUT_FILE, "r") as f:
        values = json.load(f)

    if not args.no_gui:
        gui = pd_gui.PDGUI(values)
        event = gui.create_gui()
        if event == "Submit":
            values = gui.return_dict_values()

    pd_launches = pd.PDLaunchUpload(values)
    pd_launches.create_dfs_from_csv()
    pd_items, hold_items = pd_launches.return_uploads()

    if not args.no_gui:
        event = gui.confirmation_gui(pd_items, hold_items)
        if event == "Cancel":
            sys.exit("Program Cancelled")
    else:
        print("\nUploading to PD Launches:\n")
        print("\n".join(pd_items))
        print("\n\nUploading to Holds:")
        print("\n".join(hold_items))

    if not args.test:
        pd_launches.upload_dfs()
        if not args.no_gui:
            gui.final_window()

    if not args.output:
        with open(INPUT_FILE, "w") as f:
            json.dump(values, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PD Launches tool.")
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run program in test mode, preventing upload to Smartsheet",
    )
    parser.add_argument(
        "-ng",
        "--no_gui",
        action="store_true",
        help="Run program without GUI",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store_true",
        help="Do not update JSON input after program run",
    )
    args = parser.parse_args()

    main(args)
