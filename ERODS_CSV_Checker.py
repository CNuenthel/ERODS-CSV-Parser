import csv
import re
import os

# TODO open a print function to allow captured data elements to be printed on text file
# TODO allow run operation to work in a cyle

WORKING_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erods")


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

    operation = input("\nPlease select an operation:\n1.Run\n2.Delete\n")

    if operation.lower() in ["run", "1"]:
        num_file_dict = {str(i): item for i, item in enumerate(dir_list, 1)}
        file_str = "\n".join([f"{i}. {filename}" for i, filename in num_file_dict.items()])
        
        csv_number = input(f"What is the number for the csv that you would like to run...\n{file_str}\n\n")
        csv_path = f"{WORKING_DIRECTORY}\\{num_file_dict[csv_number]}"
    
        pattern = "Inactive|Unidentified|PC|Active"
        
        non_driving_categories = ["Sleeper Berth", "Power-up", "On-duty, not driving", "Off-duty", "PC/YM Cleared", "Shut-down"]
        driving_categories = ["Driving", "Intermediate log", "PC"]
        
        try:
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)

                last_status = None
                last_odo = 0
                moving = None
                
                for row in reader:
            # Catch odd ELD csv output
                    if 'ELD File Header Segment:' in row:
                        print("Header file detected, this data format cannot be read by this script")
                        break

                    # Check for pattern keywords in RODs
                    item = RowData(row)
                    if re.search(pattern, item.status):
                        print(item.date, item.time_stamp, item.status)

                    if last_odo == 0 and item.odometer:
                        last_odo = item.odometer

                    # Continuously update odometer in moving categories
                    if item.status in driving_categories and item.odometer:
                        if moving == False:
                        
                            if item.odometer != last_odo:
                                moving = True
                                print(item.date, item.time_stamp, item.status, last_odo, item.odometer, "Possible Odo Skip")
                            
                        if item.odometer != "Missing power-up event":
                            last_odo = item.odometer
                        
                        moving = True
                        continue 

                    elif item.status in non_driving_categories and item.odometer:
                            
                        if moving == False:
                            continue
                        # First instantiation of end of movement
                        if item.odometer != "Missing power-up event":
                            last_odo = item.odometer
                        moving = False
                        continue 
                        
            print("Complete\n\n")

        except FileNotFoundError:
            dir_list = os.listdir(WORKING_DIRECTORY)    
            print("That csv filename was not located in the current directory, please try again, selecting a valid .csv file in this directory")

    elif operation.lower() in ["delete", "2"]:
        num_file_dict = {str(i): item for i, item in enumerate(dir_list, 1)}
        file_str = "\n".join([f"{i}. {filename}" for i, filename in num_file_dict.items()])
        csv_number = input(f"What is the number fo the csv that you would like to delete...\n{file_str}\n\n")
        csv_path = f"{WORKING_DIRECTORY}\\{num_file_dict[csv_number]}"
        try:
            os.remove(csv_path)
            print(f"{num_file_dict[csv_number]} has been deleted")
        except FileNotFoundError:
            print(f"Sorry the file {num_file_dict[csv_number]} was not found.")

    else:
        print("Please select an operation, Run or Delete")


if __name__ == "__main__":
    print("Welcome to the ERODS CSV Checker!\n\n")
    while True:
        run()
