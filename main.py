import os
import sys
import asyncio
import traceback
import logging
from pathlib import Path

import discord
from discord.ext import commands

from constants import variables as var

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Streamio(commands.Bot):
    """The Bot Streamio created by Chibli
    
    Created with the usage of discord.py-rewrite by Rapptz
    """

    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description", ""),
            case_insenitive=True,
            activity=kwargs.pop("activity", None),
            command_prefix=kwargs.pop("prefix", "!")
        )

        if kwargs:
            raise TypeError("Unknown kwargs passed to Bot")

        self.logger = logger
        self.loop.create_task(self.load_all_extension())

    async def load_all_extension(self):
        cogs = Path("./cogs")
        for cog in cogs.iterdir():
            if cog.suffix == ".py" and cog.stem != "__init__":
                path = ".".join(cog.with_suffix("").parts)
                try:
                    self.load_extension(path)
                    print(f"Loaded {path} successfully")
                    logger.info(f"Loaded {path} successfully")
                except Exception as e:
                    logger.error(f"Failed to load {path}")
                    print(f"Failed to load {path}")
                    print(e)

async def run():
    desc = """Streamio, the bot for all your streaming needs on discord
    Created by Chibli#0001"""

    bot_params = {
        "prefix": ":",
        "description": desc
    }

    bot = Streamio(**bot_params)

    try:
        await bot.start(var.TOKEN)
    except KeyboardInterrupt:
        #await db.close()
        await bot.logout()
        logger.warning("Bot was forcefully closed")


if __name__ == "__main__":
    os.system("CLS")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
