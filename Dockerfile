# Base image - uses Python 3.9 with a slim version (minimal OS packages)
FROM python:3.9-slim

# Sets the working directory inside the container to /app
WORKDIR /app

# Installs system-level dependencies:
# - apt-get update: Updates package list
# - gcc: Required for compiling some Python packages
# - && rm -rf...: Cleans up apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copies your requirements.txt into the container
COPY requirements.txt .
# Installs all Python dependencies
# --no-cache-dir reduces image size by not caching pip packages
RUN pip install --no-cache-dir -r requirements.txt

# Copies all your Python files into the container
COPY save_evolution.py .
COPY convert_evo_csv_to_json.py .
COPY ordinals_parser.py .
COPY node_config.py .

# Copies your data file
COPY layer_map.txt .

# Creates the evolutions directory in the container
RUN mkdir -p evolutions

# Install Flask
COPY server.py .

# Expose the port
EXPOSE 5000

# Use a shell script to run both processes
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"] 