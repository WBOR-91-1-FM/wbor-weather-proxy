"""
Proxy our Tomorrow.io API calls. Polls the API and caches results.
Hardcoded to return data for Brunswick, ME.

Author: Mason Daugherty <@mdrxy>
Version: 1.1.1
Last Modified: 2025-05-05

Changelog:
    - 1.0.0 (2025-03-23): Initial release.
    - 1.0.1 (2025-04-05): Fixes, refactoring, and indicate in response
        whether stale data was returned.
    - 1.0.2 (2025-04-15): Make the cache duration configurable via an
        environment variable.
    - 1.1.0 (2025-05-05): Added exponential backoff and increase default
        cache duration to 6 minutes (10 reqs/hr).
    - 1.1.1 (2025-05-05): Re-added Discord notifications on rate-limit
        events.
"""

import asyncio
import logging
import os
import random
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

BRUNSWICK_ME = "43.905979,-69.963375"

# Cache store and config
CACHE = {"data": None, "timestamp": 0}
CACHE_DURATION = os.environ.get("CACHE_DURATION", 360)  # seconds

# Track if we've already notified on rate limit in this window
STATE = {"rate_limit_notified": False}

TOMORROW_API_KEY = os.environ.get("TOMORROW_API_KEY")
if not TOMORROW_API_KEY:
    logger.error("TOMORROW_API_KEY is not set. Exiting.")
    sys.exit(1)


async def fetch_with_backoff(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    session, url, params, max_retries=5, base_delay=1, max_delay=60, jitter=0.5
):
    """
    Fetch data from the given URL with exponential backoff for rate
    limiting.
    """
    delay = base_delay
    for attempt in range(max_retries):
        try:
            resp = await session.get(url, params=params)
        except aiohttp.ClientError as e:
            logger.error("Fetch attempt %d failed: %s", attempt + 1, e)
        else:
            if resp.status == 429:
                # Notify once per window via Discord webhook
                if not STATE["rate_limit_notified"]:
                    await send_webhook("⚠️ Rate-limited by Tomorrow.io API")
                    STATE["rate_limit_notified"] = True

                logger.warning(
                    "Attempt %d: rate limited, retry in %.1f sec", attempt + 1, delay
                )
                await asyncio.sleep(delay + random.uniform(0, jitter))
                delay = min(delay * 2, max_delay)
                continue

            resp.raise_for_status()
            return await resp.json()

    abort(429, description="Rate-limited after retries")


@app.route("/weather", methods=["GET"])
async def get_weather():
    """
    Fetch weather data from Tomorrow.io and return it as JSON.
    """
    now = time.time()

    # Return cached data if it's still fresh
    if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_DURATION):
        logger.debug("Returning cached data")
        return jsonify(CACHE["data"])

    params = {
        "apikey": TOMORROW_API_KEY,
        "location": BRUNSWICK_ME,
        "timesteps": "1m",
        "units": "imperial",
        "fields": "temperature,weatherCode",
    }

    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch_with_backoff(
                session,
                "https://api.tomorrow.io/v4/timelines",
                params,
            )
    except aiohttp.ClientError as e:
        logger.error("Final fetch error: %s", e)
        abort(502, description="Failed to fetch data")

    # Clear notification flag once we have a successful call
    if STATE["rate_limit_notified"]:
        logger.info("Rate-limit cleared, resuming normal requests")
        STATE["rate_limit_notified"] = False

    # Update cache
    CACHE["data"] = data
    CACHE["timestamp"] = now
    logger.debug("Fetched fresh data from Tomorrow.io")

    return jsonify(data)
