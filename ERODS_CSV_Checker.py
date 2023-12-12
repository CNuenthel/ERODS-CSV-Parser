import csv
import re
import os
import sys
from pathlib import Path
from colorama import Fore, Style

# Establish standard path for erods file reading
WORKING_DIRECTORY = Path(os.getcwd())


# Helper function to sort and return a string into only its numbers
def format_number_string(num_str: str) -> int:
    return int(re.sub(r',', '', num_str))


# This setup is functional for outputs that contain solely event list data
class RowData:
    def __init__(self, csv_dict: dict):
        self.date = csv_dict['Date']
        self.time_stamp = csv_dict['Time']
        self.coord = csv_dict['Location']
        self.odometer = csv_dict['Odometer']
        self.engine_hours = csv_dict['Eng Hours']
        self.status = csv_dict['Event Type/Status']
        self.input_unit = csv_dict['Origin']
        self.id = csv_dict['Sequence #']

    def __str__(self):
        return f"Date: {self.date}, Time: {self.time_stamp}, Coord: {self.coord}, Odo: {self.odometer}, Eng Hours: {self.engine_hours}, Status: {self.status}, Input: {self.input_unit}, Id: {self.id}"


def run():
    csv_list = os.listdir(WORKING_DIRECTORY / "erods")

    operation = input(f"\n{Fore.BLUE + 'Please select an operation'}:\n"
                      f"--------------------------{Style.RESET_ALL}\n"
                      f"1.{Fore.GREEN + 'Run'}{Style.RESET_ALL}\n"
                      f"2.Delete CSV\n"
                      f"3.Quit\n"
                      f"{Fore.BLUE + '--------------------------'}{Style.RESET_ALL}\n")

    if operation.lower() in ["run", "1"]:
        data = []
        num_file_dict = {str(i): item for i, item in enumerate(csv_list, 1)}
        file_str = "\n".join([f"{i}. {filename}" for i, filename in num_file_dict.items()])

        while True:
            csv_number = input(f"\n{Fore.BLUE + 'Select an ERODs csv file.'}\n"
                               f"-------------------------{Style.RESET_ALL}"
                               f"\n{file_str}\n"
                               f"{Fore.BLUE + '-------------------------'}{Style.RESET_ALL}\n")

            if csv_number not in num_file_dict.keys():
                print("\nPlease input the corresponding number to the csv file you would like to run.")

            else:
                break

        csv_path = f"{WORKING_DIRECTORY / 'erods'}\\{num_file_dict[csv_number]}"
        pattern = "Inactive|Unidentified|PC|Active"

        non_driving_categories = ["Sleeper Berth", "Power-up", "On-duty, not driving", "Off-duty", "PC/YM Cleared",
                                  "Shut-down"]
        driving_categories = ["Driving", "Intermediate log", "PC"]

        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            last_odo = 0
            moving = False
            for row in reader:
                # Catch odd ELD csv output
                if 'ELD File Header Segment:' in row:
                    print("Header file detected, this data format cannot be read by this script")
                    break

                # Check for pattern keywords in RODs
                item = RowData(row)
                if re.search(pattern, item.status):
                    data.append(f"{item.date} {item.time_stamp} {item.status}")
                    print(item.date, item.time_stamp, item.status)

                if last_odo == 0 and item.odometer:
                    last_odo = item.odometer

                # Continuously update odometer in moving categories
                if item.status in driving_categories and item.odometer:
                    if not moving:
                        if item.odometer != last_odo:
                            moving = True
                            if item.odometer != "Missing power-up event" and last_odo != "Missing power-up event":
                                delta = format_number_string(item.odometer) - format_number_string(last_odo)

                                if delta not in [-1, 1]:
                                    data.append(
                                        f"{item.date} {item.time_stamp} {item.status} {last_odo} -> {item.odometer} [{delta} miles] Possible Odo Skip")
                                    print(item.date, item.time_stamp, item.status, last_odo, "->", item.odometer,
                                          f"[{delta} miles]", "Possible Odo Skip")
                                    continue
                                elif delta in [-1, 1]:
                                    continue

                            data.append(f"{item.date} {item.time_stamp} {item.status} {last_odo} {item.odometer}")
                            print(item.date, item.time_stamp, item.status, last_odo, item.odometer,
                                  "Possible Odo Skip")

                    if item.odometer != "Missing power-up event":
                        last_odo = item.odometer

                    moving = True
                    continue

                elif item.status in non_driving_categories and item.odometer:
                    if not moving:
                        continue

                    # First instantiation of end of movement
                    if item.odometer != "Missing power-up event":
                        last_odo = item.odometer

                    moving = False
                    continue

        print(f"\n** {Fore.MAGENTA + 'Complete'}{Style.RESET_ALL} **\n")

        # TODO complete file saving operations
        save_data = input("Save results to file? Y/N\n")

        if save_data.lower() == "y":
            # Save data to folder
            with open(WORKING_DIRECTORY / f"{num_file_dict[csv_number][:-4]}.txt", "w") as f:
                f.write("\n".join(data))

            print(f"\n{Fore.GREEN}Data saved to {num_file_dict[csv_number][:-4]}.txt{Style.RESET_ALL}")

    elif operation.lower() in ["delete", "2"]:
        csv_list.append("Cancel") # Add cancel to the list to allow for cancellation operation

        num_file_dict = {str(i): item for i, item in enumerate(csv_list, 1)}
        file_str = "\n".join([f"{i}. {filename}" for i, filename in num_file_dict.items()])

        while True:
            csv_number = input(f"\n{Fore.BLUE + 'Select a csv file to delete or cancel.'}\n"
                               f"--------------------------------------------------------------{Style.RESET_ALL}\n"
                               f"{file_str}\n"
                               f"{Fore.BLUE + '--------------------------------------------------------------'}{Style.RESET_ALL}\n")

            if csv_number not in num_file_dict.keys():
                print("\nPlease input the corresponding number to the csv file you would like to delete.")
            else:
                break

        if num_file_dict[csv_number] == "Cancel":
            print("\nOperation Canceled...")
            return

        csv_path = f"{WORKING_DIRECTORY / 'erods'}\\{num_file_dict[csv_number]}"

        try:
            os.remove(csv_path)
            print(f"{num_file_dict[csv_number]} has been deleted")
        except FileNotFoundError:
            print(f"Sorry the file {num_file_dict[csv_number]} was not found.")

    elif operation.lower() in ["quit", "3"]:
        sys.exit()

    else:
        print("Please select a valid operation, Run, Delete, or Quit")


if __name__ == "__main__":
    print("Welcome to the ERODS CSV Checker!")
    while True:
        run()
