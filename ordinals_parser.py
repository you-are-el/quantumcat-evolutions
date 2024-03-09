import requests
from bitcoin.rpc import RawProxy
from node_config import (USE_PUBLIC_API, PUBLIC_API_ENDPOINT, FALLBACK_API_ENDPOINT,
                    LOCAL_NODE_RPC_URL, LOCAL_NODE_RPC_USER, LOCAL_NODE_RPC_PASSWORD)

def get_blockchain_info(timeout_duration=2):
    if USE_PUBLIC_API:
        print("Error: This function is only available when using a local node.")
        return None
    else:
        # Use local node
        service_url = f'http://{LOCAL_NODE_RPC_USER}:{LOCAL_NODE_RPC_PASSWORD}@{LOCAL_NODE_RPC_URL}'
        p = RawProxy(service_url=service_url)
        try:
            blockchain_info = p.getblockchaininfo()
            return blockchain_info
        except Exception as e:
            print(f"Local node RPC error: {e}")
            return None

def get_full_transaction_from_tx_id(tx_id, timeout_duration=2):
    if USE_PUBLIC_API:
        # Try primary public API
        try:
            primary_url = f"{PUBLIC_API_ENDPOINT}tx/{tx_id}"
            primary_response = requests.get(primary_url, timeout=timeout_duration)
            primary_response.raise_for_status()
            return primary_response.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
            print("Primary public API failed. Attempting fallback public API.")
            # Try fallback public API
            try:
                fallback_url = f"{FALLBACK_API_ENDPOINT}tx/{tx_id}"
                fallback_response = requests.get(fallback_url, timeout=timeout_duration)
                fallback_response.raise_for_status()
                return fallback_response.json()
            except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
                print("Fallback public API also failed.")
                return None
    else:
        # Use local node
        service_url = f'http://{LOCAL_NODE_RPC_USER}:{LOCAL_NODE_RPC_PASSWORD}@{LOCAL_NODE_RPC_URL}'
        p = RawProxy(service_url=service_url)
        try:
            raw_tx = p.getrawtransaction(tx_id)
            decoded_tx = p.decoderawtransaction(raw_tx)
            return decoded_tx
        except Exception as e:
            print(f"Local node RPC error: {e}")
            return None

def get_block_data_from_tx_id(tx_id, timeout_duration=2):
    if USE_PUBLIC_API:
        try:
            tx = get_full_transaction_from_tx_id(tx_id, timeout_duration)
            block_hash = tx['status']['block_hash']
            primary_url = f'{PUBLIC_API_ENDPOINT}block/{block_hash}'
            primary_response = requests.get(primary_url, timeout=timeout_duration)
            primary_response.raise_for_status()
            return primary_response.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
            print("Primary source failed. Attempting to get block data from the secondary source.")
            fallback_url = f'{FALLBACK_API_ENDPOINT}block/{block_hash}'
            fallback_response = requests.get(fallback_url, timeout=timeout_duration)
            fallback_response.raise_for_status()
            return fallback_response.json()
    else:
        # Use local node
        service_url = f'http://{LOCAL_NODE_RPC_USER}:{LOCAL_NODE_RPC_PASSWORD}@{LOCAL_NODE_RPC_URL}'
        p = RawProxy(service_url=service_url)
        try:
            # Fetch the block hash using the transaction ID
            # Note: This might require a different approach depending on how the local node RPC is set up
            raw_tx = p.getrawtransaction(tx_id, 1)  # 1 for verbose output
            block_hash = raw_tx.get('blockhash', None)
            if block_hash:
                block_data = p.getblock(block_hash)
                return block_data
            else:
                print("Block hash not found in the transaction data.")
                return None
        except Exception as e:
            print(f"Local node RPC error: {e}")
            return None

def get_witness_data_from_tx_id(tx_id, timeout_duration=2):
    if USE_PUBLIC_API:
        try:
            primary_url = f'{PUBLIC_API_ENDPOINT}tx/{tx_id}'
            primary_response = requests.get(primary_url, timeout=timeout_duration)
            primary_response.raise_for_status()
            tx_witness = ''.join(primary_response.json()['vin'][0]['witness'])
            return tx_witness
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
            print("Primary source failed. Attempting to get witness data from the secondary source.")
            fallback_url = f'{FALLBACK_API_ENDPOINT}tx/{tx_id}'
            fallback_response = requests.get(fallback_url, timeout=timeout_duration)
            fallback_response.raise_for_status()
            # Adjust parsing if needed
            tx_witness = ''.join(fallback_response.json()['vin'][0]['witness'])
            return tx_witness
    else:
        # Use local node
        service_url = f'http://{LOCAL_NODE_RPC_USER}:{LOCAL_NODE_RPC_PASSWORD}@{LOCAL_NODE_RPC_URL}'
        p = RawProxy(service_url=service_url)
        try:
            raw_tx = p.getrawtransaction(tx_id, 1)  # 1 for verbose output
            for vin in raw_tx.get('vin', [{}]):
                tx_witness = ''.join(vin.get('txinwitness', []))
                if find_envelope_and_inscription(tx_witness)[1]:
                    return tx_witness
        except Exception as e:
            print(f"Local node RPC error: {e}")
            return None

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_ascii(byte_data):
    return byte_data.decode('ascii')

def mime_type_to_extension(mime_type):
    # Mapping common MIME types to file extensions
    mapping = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/webp': 'webp',
        'image/gif': 'gif',
        'text/plain': 'txt',
        'text/plain;charset=utf-8': 'txt',
        'text/html;charset=utf-8': 'html',
        'text/x-python': 'py',
        'video/mp4': 'mp4',
        'audio/mpeg': 'mpeg',
        'model/gltf-binary': 'glb',
        'image/svg+xml': 'svg',
        'application/octet-stream': 'webp',
        # Add more mappings as needed
    }
    return mapping.get(mime_type, 'bin')  # Default to 'bin' for binary data

def find_envelope_and_inscription(hex_string):
    # Define the envelope format and opcodes in hex
    OP_FALSE = '00'
    OP_IF = '63'
    ORD = '036f7264'
    OP_1 = '0101'
    OP_0 = '00'
    OP_PUSHDATA1 = '4c'
    OP_PUSHDATA2 = '4d'
    OP_PUSHDATA4 = '4e'
    OP_ENDIF = '68'

    # Search for the envelope start
    envelope_start_seq = OP_FALSE + OP_IF + ORD + OP_1
    start_index = hex_string.find(envelope_start_seq)
    if start_index == -1:
        print("Envelope start sequence not found.")
        return None, None

    # Extract MIME type description
    mime_type_length_index = start_index + len(envelope_start_seq)
    mime_type_length_hex = hex_string[mime_type_length_index:mime_type_length_index + 2]
    mime_type_length = int(mime_type_length_hex, 16) * 2  # Length in characters
    mime_type_start = mime_type_length_index + 2
    mime_type_end = mime_type_start + mime_type_length
    mime_type_hex = hex_string[mime_type_start:mime_type_end]
    mime_type = bytes.fromhex(mime_type_hex).decode('ascii')

    # Find and collect inscription data chunks
    data_start = mime_type_end + 2  # Skipping OP_0
    inscription_data = ''
    while hex_string[data_start:data_start + 2] != OP_ENDIF:
        opcode_hex = hex_string[data_start:data_start + 2]
        opcode = int(opcode_hex, 16)
        data_start += 2
        chunk_length = 0
        if '01' <= opcode_hex <= '4b':  # Direct push of 1-75 bytes
            chunk_length = opcode * 2  # Length in characters
        elif opcode_hex in [OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4]:
            length_bytes = 2 if opcode_hex == OP_PUSHDATA1 else 4 if opcode_hex == OP_PUSHDATA2 else 8
            chunk_length_hex = hex_string[data_start:data_start + length_bytes]
            # Convert hex string to byte array in little-endian format and get length
            chunk_length = int.from_bytes(bytes.fromhex(chunk_length_hex), 'little') * 2
            data_start += length_bytes
        else:
            print("Unexpected data format in inscription.")
            break

        chunk_start = data_start
        chunk_end = chunk_start + chunk_length
        inscription_data += hex_string[chunk_start:chunk_end]
        data_start = chunk_end

    # Return the MIME type and inscription data in hex format
    return mime_type, inscription_data


def inscription_data_to_file(mime_type, hex_string, output_file):
    # Convert hex string to bytes
    binary_data = bytes(int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2))

    # Determine the file extension
    extension = mime_type_to_extension(mime_type)
    output_file_with_extension = f"{output_file}.{extension}"

    # Save binary data to a file
    with open(output_file_with_extension, 'wb') as file:
        file.write(binary_data)