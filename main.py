from datetime import datetime
import os
import sys
from parsers import FileNameToDateParser


def change_file_modification_date(file: str, date: datetime):
    os.utime(file, (datetime.now().timestamp(), date.timestamp()))


def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python3 main.py path [date]")
        print()
        print("  If a date is specified, only files last modified on this date are corrected.")
        print("  Date format: 2024-08-26")
        sys.exit(1)

    try:
        selected_modification_date_filter = datetime.fromisoformat(sys.argv[2])
    except IndexError:
        selected_modification_date_filter = None

    answer = input("This will change the modifications date of the files in the given path.\nYou might want to make a backup first. Continue? [y/N] ")
    if answer.lower() not in ['y', 'yes']:
        sys.exit(0)

    dirname = sys.argv[1]
    files = os.scandir(path=dirname)
    for file in files:
        if not file.is_file():
            continue
        if selected_modification_date_filter:
            modi_time_timestamp = os.stat(file).st_mtime
            modi_time = datetime.fromtimestamp(modi_time_timestamp)
            # If the modification date of the currently iterated file
            # is not what the user specified, just skip it without touching it.
            if modi_time.date() != selected_modification_date_filter.date():
                continue

        parser_name, date = FileNameToDateParser.try_parse_with_all(file.name)
        if date is not None:
            change_file_modification_date(file.path, date)
            print(f"{file.name:>30} -> {str(date):<30} ({parser_name})")
        else:
            print(f"{file.name:>30} -> ???")


if __name__ == "__main__":
    main()
