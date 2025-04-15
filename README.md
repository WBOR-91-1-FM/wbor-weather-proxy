# wbor-weather-proxy

This repository provides a very barebones Dockerized API proxy for [Tomorrow.io](https://tomorrow.io) weather data. By default, it caches responses for 60 seconds to reduce latency and minimize requests to the external API. This value set via an environment variable as needed (`CACHE_DURATION`). If the container is rate limited, a Discord webhook will be triggered to notify the team.

## Overview

* Cache: In-memory cache with a 60-second TTL (adjustable via `CACHE_DURATION` environment variable)
* API: RESTful API with a single endpoint `/weather` that proxies requests to the Tomorrow.io API
  * Hard coded for our station's location (`BRUNSWICK_ME`)
* Notifications: Discord webhook for rate limit notifications
* Docker: Dockerized for easy deployment and scaling

## Requirements

* Docker installed
* Make installed (optional, but recommended)
* A Discord webhook URL (optional, for rate limit notifications)
* A Tomorrow.io API key (required)

## Setup

1. Clone this repository

    ```sh
    git clone https://github.com/WBOR-91-1-FM/wbor-weather-proxy.git
    cd wbor-weather-proxy
    ```

2. Create a `.env` file in the root directory with the following content:

   ```sh
   TOMORROW_API_KEY=your-api-key-here
   ```

   Optionally, you can set the `CACHE_DURATION` variable to change the cache duration (in seconds). For example, to set it to 120 seconds:

   ```sh
   CACHE_DURATION=120
   ```

   Finally, if you want to set up Discord notifications for rate limits, set the `DISCORD_WEBHOOK_URL` variable in the `.env` file:

   ```sh
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
    ```

3. (Optional) Update the coordinates in app.py if you need weather for somewhere else.

## Building and Running

The included Makefile has targets for building and running the Docker container. You can also run the commands manually if you don't have Make installed.

## Usage

Once running, the endpoint will be available at `http://localhost:4321/weather`. You can test it by running:

```sh
curl http://localhost:4321/weather
```

You may wish to remove the port mapping if you are running this in a production environment. The default port is `4321`, but you can change it in the `Makefile`.
