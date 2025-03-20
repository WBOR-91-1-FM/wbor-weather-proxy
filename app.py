"""
Proxy our Tomorrow.io API calls. Polls the API and caches results for 60
seconds. Hard coded to return data from Brunswick, ME.

Author: Mason Daugherty <@mdrxy>
Version: 1.0.0
Last Modified: 2025-03-23

Changelog:
    - 1.0.0 (2025-03-23): Initial release.
"""

import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_DURATION = 60  # seconds

TOMORROW_API_KEY = os.environ.get("TOMORROW_API_KEY")
if not TOMORROW_API_KEY:
    log.error("TOMORROW_API_KEY is not set. Exiting.")
    sys.exit(1)


@app.route("/weather", methods=["GET"])
def get_weather():
    """
    Fetch weather data from Tomorrow.io and return it as JSON.
    """
    now = time.time()
    # Return cached data if fresh
    if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_DURATION):
        log.info("Returning cached data")
        return jsonify(CACHE["data"])

    params = {
        "apikey": TOMORROW_API_KEY,
        "location": "41.3276,-72.7673",
        "timesteps": "1m",
        "units": "imperial",
        "fields": "temperature,weatherCode",
    }
    try:
        response = requests.get(
            "https://api.tomorrow.io/v4/timelines", params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        log.error("Error fetching data from Tomorrow.io: `%s`", e)
        abort(502, description="Failed to fetch data")

    CACHE["data"] = data
    CACHE["timestamp"] = now
    log.info("Fetched fresh data from Tomorrow.io")
    return jsonify(data)
