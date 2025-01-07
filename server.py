from flask import Flask, send_file, jsonify
import os
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_evolution_script():
    try:
        logger.info("Starting evolution script...")
        subprocess.run(["python", "save_evolution.py"], check=True)
        logger.info("Evolution script completed successfully")
    except Exception as e:
        logger.error(f"Error running evolution script: {e}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_evolution_script, trigger="interval", minutes=9)
scheduler.start()

@app.route('/cat_evolution.json')
def serve_evolution():
    try:
        return send_file('cat_evolution.json', mimetype='application/json')
    except FileNotFoundError:
        return jsonify({"error": "Evolution file not found"}), 404

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "next_run": scheduler.get_jobs()[0].next_run_time
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 