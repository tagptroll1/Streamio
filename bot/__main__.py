import os
import sys
import json
import asyncio
import traceback
import logging
import datetime
from pathlib import Path

import discord
from discord.ext import commands

Path("./logs").mkdir(exist_ok=True)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=f'logs/discord {datetime.datetime.today().strftime("%B %d, %Y")}.log', 
    encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Streamio(commands.AutoShardedBot):
    """The Bot Streamio created by Chibli
    
    Created with the usage of discord.py-rewrite by Rapptz
    """

    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description", ""),
            case_insenitive=True,
            activity=kwargs.pop("activity", None),
            command_prefix=commands.when_mentioned_or(*kwargs.pop("prefix", ["!"]))
        )

        if kwargs:
            raise TypeError("Unknown kwargs passed to Bot")

        self.logger = logger
        self.start_time = None
        self.app_info = None
        self.blacklist = dict()
        self.swearlist = dict()
        self.msg_log = []

        with open("swearjar.json") as data:
            self.swearjar = json.load(data)[0]

    async def track_start(self):
        """Ready Check and timestamper

        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        

    def load_all_extension(self):
        cogs = Path("./cogs")

        for cog in cogs.iterdir():
            if cog.is_dir():
                continue
            if cog.suffix == ".py":
                if cog.stem == "__init__":
                    continue
                elif cog.stem == "database":
                    continue

                path = ".".join(cog.with_suffix("").parts)
                try:
                    self.load_extension(path)
                    print(f"Loading... {path:<22} Success!")
                    logger.info(f"Loading... {path:<22} Success!")
                except Exception as e:
                    logger.exception(f"\nLoading... {path:<22} Failed!")
                    print("-"*25)
                    print(f"Loading... {path:<22} Failed!")
                    print(e, "\n" , "-"*25, "\n")

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        if not self.start_time:
            await self.wait_until_ready()
            self.start_time = datetime.datetime.utcnow()

        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n')
        print('-' * 10)

    async def logout(self):
        """|coro|
        Logs out of Discord and closes all connections.
        """
        with open("swearjar.json", "w") as data:
            json.dump([self.swearjar], data)

        await super().logout()

def run():
    desc = (
        "Streamio, the bot for all your streaming needs on discord\n"
        "Created by Chibli#0001"
    )

    bot_params = {
        "prefix": ["!!","??"],
        "description": desc,
    }

    bot = Streamio(**bot_params)

    if var.TOKEN is None:
        logger.critical("Token is not set!")
        sys.exit(1)

    bot.load_all_extension()

    try:
        bot.run(var.TOKEN)
    except discord.LoginFailure:
        logger.critical("Invalid token")
    finally:
        sys.exit(1)


if __name__ == "__main__":
    os.system("CLS")
    run()
