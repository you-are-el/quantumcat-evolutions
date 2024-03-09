import ordinals_parser as ord
import convert_evo_csv_to_json as evo_converter
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import io
from PIL import Image
import json
import random
import csv
from collections import Counter, defaultdict
import os
import pandas as pd
import shutil
import tempfile
import datetime

def read_cat_map(file_path):
    """
    Reads the cat_map.txt file and returns a list of tuples with folder names and inscription IDs.
    """
    cat_map = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                cat_map.append((parts[0], parts[1]))
    return cat_map

def download_and_process_data(inscription_id):
    """
    Downloads the JSON file using the inscription ID, decrypts and decodes the data,
    and stores it in the specified folder. Placeholder for your existing code or logic.
    """
    # Your code to download the JSON from the blockchain using the inscription ID
    # Your code to decrypt and decode the data
    # Example: decrypted_data = decrypt_and_decode(json_data)
    
    return get_layer_map_from_json_inscription(inscription_id)

def get_layer_map_from_json_inscription(json_inscription_id):
    """
    Extracts the transaction IDs from the JSON inscription.

    :param json_inscription: The JSON inscription to extract the transaction IDs from.
    :return: A list of transaction IDs.
    """
    json_inscription_hash = json_inscription_id[:-2]
    witness_data = ord.get_witness_data_from_tx_id(json_inscription_hash)
    mime_type, inscription = ord.find_envelope_and_inscription(witness_data)
    json_data = ord.bytes_to_ascii(ord.hex_to_bytes(inscription))
    # Parse the JSON data
    parsed_json = json.loads(json_data)

    # Access the 'layerTraitMap' entries
    layer_hex_IV = parsed_json.get("layerHexIV", {})
    layer_hey_key = parsed_json.get("layerHexKey", {})
    layer_trait_map = parsed_json.get("layerTraitMap", {})
    layer_map = parsed_json.get("layerMap", {})

    return layer_map



cat_map_file = 'layer_map.txt'
cat_map = read_cat_map(cat_map_file)

# Initialize the DataFrame
columns = ['catid'] + [f'layer{i}' for i in range(1, 41)]
df = pd.DataFrame(columns=columns)

# Populate the catid column
df['catid'] = [f'cat{str(i).zfill(4)}' for i in range(3333)]

for layer, inscription_id in cat_map:
    print(f"Processing inscription: {layer} with ID: {inscription_id}")
    layer_column = layer
    try:
        layer_map = download_and_process_data(inscription_id)
        
        # Diagnostic print statements
        print(f"Number of cats in layer_map for layer {layer}: {len(layer_map)}")
        if layer == 1:  # Assuming layer 1 is where you expect all True
            print("Sample of layer_map for layer 1:", list(layer_map.items())[:5])  # Print first 5 items for checking

        df[layer_column] = df['catid'].apply(lambda catid: catid in layer_map)
    except Exception as e:
        print(f"Error processing inscription ID {inscription_id}: {e}")
        df[layer_column] = None


# Save df to csv
def get_latest_file(folder_path, base_name='evo'):
    """
    Returns the path to the latest (highest numbered) CSV file in the specified folder.
    """
    csv_files = [f for f in os.listdir(folder_path) if f.startswith(base_name) and f.endswith('.csv')]
    if not csv_files:
        return None
    latest_file_number = max([int(f.replace(base_name, '').replace('.csv', '')) for f in csv_files])
    latest_file_name = f"{base_name}{latest_file_number}.csv"
    print(latest_file_name)
    return os.path.join(folder_path, latest_file_name)

def dataframe_content_check(new_df, existing_df):
    """
    Checks that the new DataFrame does not have NaN values in any cell where the existing DataFrame has non-NaN values.
    Assumes columns are the same and in the same order in both DataFrames.
    """
    print(new_df.head(5))
    print(existing_df.head(5)) 
    for column in existing_df.columns:
        # Identify where existing_df has non-NaN values
        non_nan_mask = existing_df[column].notna()
        
        # For those positions, check if new_df also has non-NaN values
        if not new_df[column][non_nan_mask].notna().all():
            # If new_df has NaN values where existing_df has non-NaN values, return False
            return False
            
    return True


def csv_files_are_identical(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        return f1.read() == f2.read()

def get_next_filename(folder_path, base_name):
    existing_files = [f for f in os.listdir(folder_path) if f.startswith(base_name) and f.endswith('.csv')]
    existing_indices = [int(f.replace(base_name, '').replace('.csv', '')) for f in existing_files]
    next_index = max(existing_indices) + 1 if existing_indices else 0
    return f"{base_name}{next_index}.csv"

# Path to the evolutions folder
evolutions_folder = 'evolutions'

with tempfile.TemporaryDirectory() as temp_dir:
    temp_filename = os.path.join(temp_dir, 'temp.csv')
    df.to_csv(temp_filename, index=False)

    duplicate_found = False
    latest_file_path = get_latest_file(evolutions_folder)
    
    if latest_file_path:
        latest_df = pd.read_csv(latest_file_path)
        new_df = pd.read_csv(temp_filename)
        if csv_files_are_identical(temp_filename, latest_file_path):
            duplicate_found = True
        elif not dataframe_content_check(new_df, latest_df):
            print("New DataFrame does not have the same content in all cells as the latest DataFrame. Not saved.")
            print("Time:", datetime.datetime.now().time())
            exit()  # Exit if the new DataFrame doesn't meet the cell content requirement
    
    if not duplicate_found:
        if latest_file_path:
            latest_number = int(latest_file_path.split('/')[-1].replace('evo', '').replace('.csv', ''))
            next_number = latest_number + 1
        else:
            next_number = 0
        next_filename = f"evo{next_number}.csv"
        final_path = os.path.join(evolutions_folder, next_filename)
        shutil.move(temp_filename, final_path)
        print(f"DataFrame saved as {next_filename}")
        print("Time:", datetime.datetime.now().time())
    else:
        print("Duplicate DataFrame. Not saved.")
        print("Time:", datetime.datetime.now().time())
        
evo_converter.convert_evo_to_json()