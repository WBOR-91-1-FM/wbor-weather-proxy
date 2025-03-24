"""
Send status messages to Discord using webhooks.
https://github.com/lovvskillz/python-discord-webhook

Author: Mason Daugherty <@mdrxy>
Version: 1.0.0
Last Modified: 2025-03-23

Changelog:
    - 1.0.0 (2025-03-23): Initial release.
"""

import os

from discord_webhook import AsyncDiscordWebhook


async def send_webhook(message: str) -> None:
    """
    Send a message to Discord using a webhook.
    """
    webhook = AsyncDiscordWebhook(
        url=os.environ.get("DISCORD_WEBHOOK_URL"), content=message
    )
    await webhook.execute()
