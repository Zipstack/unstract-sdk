#!/usr/bin/env python
import argparse
import shutil
from importlib.resources import files
from pathlib import Path


def new_tool(args):
    tool_name = args.tool_name
    if tool_name is None:
        print("Tool name is required")
        exit(1)
    location = args.location
    if location is None:
        print("Location is required")
        exit(1)
    overwrite = args.overwrite
    print(f"Creating new tool {tool_name} at {location}")
    # Check if folder exists
    folder = Path(location).joinpath(tool_name)
    if folder.exists():
        if overwrite:
            print("Folder exists, overwriting")
        else:
            print("Folder exists, exiting")
            exit(1)
    else:
        folder.mkdir(parents=True, exist_ok=True)

    source = Path(files("unstract.sdk").joinpath("static/tool_template/v1/"))
    print(f"Copying files from {source} to {folder}")
    # Copy all files in source to folder, recursively
    shutil.copytree(source, folder, dirs_exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="Unstract tool generator",
        description="Script to generate a new Unstract tool",
        epilog="Unstract SDK",
    )
    parser.add_argument(
        "--command", type=str, help="Command to execute", required=True
    )
    parser.add_argument(
        "--tool-name", type=str, help="Tool name", required=False
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Director to create the new tool in",
        required=False,
    )
    parser.add_argument(
        "--overwrite",
        help="Overwrite existing tool",
        required=False,
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    command = str.upper(args.command)

    if command == "NEW":
        try:
            new_tool(args)
        except Exception as e:
            print(f"Error creating new tool: {e}")
            exit(1)
        print("New tool created successfully")
    else:
        print("Command not supported")
        exit(1)


if __name__ == "__main__":
    main()
