from datetime import datetime
import os
import sys
from parsers import FileNameToDateParser


def change_file_modification_date(file: str, date: datetime):
    os.utime(file, (datetime.now().timestamp(), date.timestamp()))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py path")
        sys.exit(1)

    answer = input("This will change the modifications date of the files in the given path.\nYou might want to make a backup first. Continue? [y/N] ")
    if answer.lower() not in ['y', 'yes']:
        sys.exit(0)

    dirname = sys.argv[1]
    files = os.scandir(path=dirname)
    for file in files:
        parser_name, date = FileNameToDateParser.try_parse_with_all(file.name)
        if date is not None:
            change_file_modification_date(file.path, date)
            print(f"{file.name:>30} -> {str(date):<30} ({parser_name})")
        else:
            print(f"{file.name:>30} -> ???")


if __name__ == "__main__":
    main()
