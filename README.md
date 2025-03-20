# wbor-weather-proxy

This repository provides a very barebones Dockerized API proxy for [Tomorrow.io](https://tomorrow.io) weather data. It caches responses for 60 seconds to reduce latency and minimize requests to the external API.

## Overview

* Cache: In-memory cache with a 60-second TTL
* API: RESTful API with a single endpoint `/weather` that proxies requests to the Tomorrow.io API
  * Hard coded for our station's location

## Requirements

* Docker installed
* Make installed (optional, but recommended)

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

3. (Optional) Update the location in app.py if you need weather for somewhere else.

## Building and Running

The included Makefile has targets for building and running the Docker container. You can also run the commands manually if you don't have Make installed.

## Usage

Once running, the endpoint will be available at `http://localhost:4321/weather`. You can test it by running:

```sh
curl http://localhost:5000/weather
```
