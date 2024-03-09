import os
import csv
import json

def convert_evo_to_json():
    # Define the path to the evolutions folder
    evolutions_folder = "evolutions"

    # Create an empty dictionary to store the JSON structure
    json_data = {}

    # Iterate through each catid
    for catid in [f"cat{i:04d}" for i in range(3333)]:
        print(f"Processing catid: {catid}")
        # Create an empty list to store the evolution states
        evolution_states = []

        # Iterate through each CSV file in the evolutions folder
        file_list = os.listdir(evolutions_folder)
        file_list.sort(key=lambda x: int(x[3:-4]) if x[3:-4].isdigit() else float('inf'))
        for filename in file_list:
            if filename.endswith(".csv"):
                # Create an empty list to store the entries for this evolution state
                entries = []

                # Read the CSV file
                with open(os.path.join(evolutions_folder, filename), "r") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    next(csv_reader)  # Skip the header row

                    # Iterate through each row in the CSV file
                    for row in csv_reader:
                        # Check if the catid in the CSV matches the current catid
                        if row[0] == catid:
                            # Read the entries for layer1-layer40 and append them to the list
                            entries.extend(row[1:41])

                # Append the entries to the evolution states list
                evolution_states.append(entries)

        # Add the evolution states to the JSON data
        json_data[str(catid)] = evolution_states

    # Convert the JSON data to a JSON string
    json_string = json.dumps(json_data)

    # Print the JSON string
    # Define the path to save the JSON file
    json_file_path = "cat_evolution.json"

    # Write the JSON string to the file
    with open(json_file_path, "w") as json_file:
        json_file.write(json_string)
