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

import aiohttp
from dotenv import load_dotenv
from quart import Quart, abort, jsonify

from utils.discord import send_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Quart(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_DURATION = 60  # seconds
STATE = {
    "rate_limit_notified": False  # Tracks if we've already sent a webhook for this cycle
}

TOMORROW_API_KEY = os.environ.get("TOMORROW_API_KEY")
if not TOMORROW_API_KEY:
    logger.error("TOMORROW_API_KEY is not set. Exiting.")
    sys.exit(1)


@app.route("/weather", methods=["GET"])
async def get_weather():
    """
    Fetch weather data from Tomorrow.io and return it as JSON.
    """
    rate_limit_notified = STATE["rate_limit_notified"]
    now = time.time()

    # Return cached data if it's still fresh
    if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_DURATION):
        logger.debug("Returning cached data")
        return jsonify(CACHE["data"])

    params = {
        "apikey": TOMORROW_API_KEY,
        "location": "43.905979,-69.963375",  # Brunswick, ME
        "timesteps": "1m",
        "units": "imperial",
        "fields": "temperature,weatherCode",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.tomorrow.io/v4/timelines", params=params
            ) as resp:
                if resp.status == 429:
                    logger.warning(
                        "Rate-limited by Tomorrow.io. Returning cached data if available."
                    )
                    if not rate_limit_notified:
                        await send_webhook("Rate-limited by Tomorrow.io")
                        STATE["rate_limit_notified"] = True

                    if CACHE["data"]:
                        stale_data = CACHE["data"].copy()
                        stale_data["stale_data_returned"] = True
                        stale_data["error_code"] = 429
                        return jsonify(stale_data)

                    abort(
                        429,
                        description="Rate-limited by Tomorrow.io, and no cached data available.",
                    )

                # If we're here, it's a successful (non-429) response.
                # Reset the rate limit flag.
                if rate_limit_notified:
                    STATE["rate_limit_notified"] = False

                resp.raise_for_status()
                data = await resp.json()

    except aiohttp.ClientError as e:
        logger.error("Error fetching data from Tomorrow.io: %s", e)
        abort(502, description="Failed to fetch data")

    CACHE["data"] = data
    CACHE["timestamp"] = now
    logger.debug("Fetched fresh data from Tomorrow.io")
    return jsonify(data)
