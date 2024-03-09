# Configuration for Public APIs
# =============================
# USE_PUBLIC_API: This flag determines the source of data retrieval.
# If True, the application will use public Mempool APIs. 
# If False, it will use a local Bitcoin node. 
# Set this based on your preference or available resources.
USE_PUBLIC_API = True  # Set to False to use a local Bitcoin node

# PUBLIC_API_ENDPOINT: The primary Mempool API endpoint for fetching Bitcoin data.
# This is always set to use 'mempool.space', the primary source for data requests.
PUBLIC_API_ENDPOINT = 'https://mempool.space/api/'

# FALLBACK_API_ENDPOINT: The fallback Mempool API endpoint.
# In case the primary API (mempool.space) is unreachable, this fallback API is used.
# This should be set to another third-party hosted Mempool API.
# Example: 'https://mempool.bullbitcoin.com/api/'
# Note: Ensure that the fallback API has a similar response format to the primary API.
FALLBACK_API_ENDPOINT = 'https://mempool.bullbitcoin.com/api/'  # Replace with another Mempool API if preferred

# Configuration for Local Bitcoin Node
# ====================================
# The following settings apply when USE_PUBLIC_API is set to False.
# Configure these to align with your local Bitcoin node settings.

# LOCAL_NODE_RPC_URL: The URL to access your local Bitcoin node's RPC interface.
# Update this with your node's IP address and RPC port.
# Default for local setups is usually 'http://127.0.0.1:8332'.
LOCAL_NODE_RPC_URL = '192.168.178.80:8332'  # Modify as needed

# LOCAL_NODE_RPC_USER: Username for RPC authentication.
# This should match the username in your Bitcoin node's bitcoin.conf.
LOCAL_NODE_RPC_USER = 'youareel'  # Replace with your RPC username

# LOCAL_NODE_RPC_PASSWORD: Password for RPC authentication.
# This should match the password in your Bitcoin node's bitcoin.conf.
LOCAL_NODE_RPC_PASSWORD = 'root'  # Replace with your RPC password