"""
Proxy for our Tomorrow.io API calls. This script will call the Tomorrow.io API
and cache the results for 60 seconds. This will prevent us from hitting the
API rate limit and will also speed up the response time for our consumers.

Hard coded to return data from Brunswick, ME. This could be made more dynamic
by accepting a lat/long as a query parameter.
"""

import os
import sys
import time
import logging
import requests
from flask import Flask, jsonify, abort
from dotenv import load_dotenv

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
