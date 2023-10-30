import csv
import re
import os
import code

# TODO open a print function to allow captured data elements to be printed on text file
# TODO allow run operation to work in a cyle

WORKING_DIRECTORY = os.path.realpath(__file__)[:-20]

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
    dir_list = os.listdir(WORKING_DIRECTORY)
    files = "\n".join([filename[:-4] for filename in dir_list if filename[-4:] == ".csv"])
    csv_name = input(f"What is the csv filename that you would like to run...\n{files}\n\n")
    pattern = "Inactive|Unidentified|PC|Active"
    csv_data = []

    try:
        csv_path = f"{WORKING_DIRECTORY}\\{csv_name}.csv"
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

        # Catch odd ELD csv output
                if 'ELD File Header Segment:' in row:
                    print("Header file detected, this data format cannot be read by this script")
                    break

                item = RowData(row)
                if re.search(pattern, item.status):
                    print(item.date, item.time_stamp, item.status)
                csv_data.append(item)

        print("Complete")

    except FileNotFoundError:
        dir_list = os.listdir(WORKING_DIRECTORY)
        files = "\n".join([filename for filename in dir_list if filename != "ERODS_CSV_Checker.py"])

        print(f"That csv filename was not located in the current directory, please try again, selecting a valid .csv file in this directory")

def delete():
    csv_name = input("What is the csv filename that you would like to delete?\n")
    os.remove(f"{WORKING_DIRECTORY}\\{csv_name}.csv")
    print(f"CSV file has been deleted!")

if __name__ == "__main__":
    print("Welcome to the ERODS CSV Checker!\n\n")
    run()
    code.interact(local=locals())
