"""
Send status messages to Discord using webhooks.
https://github.com/lovvskillz/python-discord-webhook

Author: Mason Daugherty <@mdrxy>
Version: 1.0.1
Last Modified: 2025-03-23

Changelog:
    - 1.0.0 (2025-03-23): Initial release.
    - 1.0.1 (2025-04-15): Only send webhook if URL is set in env.
"""

import os

from discord_webhook import AsyncDiscordWebhook


async def send_webhook(message: str) -> None:
    """
    Send a message to Discord using a webhook, if the webhook URL is set
    in the environment variables. Otherwise, do nothing.
    """
    url = os.environ.get("DISCORD_WEBHOOK_URL")

    if url:
        webhook = AsyncDiscordWebhook(url=url, content=message)
        await webhook.execute()
