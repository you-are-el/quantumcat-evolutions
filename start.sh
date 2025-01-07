#!/bin/bash

# Start the evolution script in the background
python save_evolution.py &

# Start the Flask server
python server.py 