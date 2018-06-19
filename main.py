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

from constants import variables as var

Path("./logs").mkdir(exist_ok=True)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=f'logs/discord {datetime.datetime.today().strftime("%B %d, %Y")}.log', 
    encoding='utf-8', mode='a')
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
        self.myloop = kwargs.pop("loop")

        if kwargs:
            raise TypeError("Unknown kwargs passed to Bot")

        self.logger = logger
        self.db = None
        self.start_time = None
        self.app_info = None
        self.blacklist = dict()
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extension())
        self.secrets = var
        with open("swearjar.json") as data:
            self.swearjar = json.load(data)[0]



    async def track_start(self):
        """Ready Check and timestamper

        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()


    async def load_all_extension(self):

        await self.wait_until_ready()
        await asyncio.sleep(1)

        cogs = Path("./cogs")
        for cog in cogs.iterdir():
            if cog.is_dir():
                continue
            if cog.suffix == ".py" and cog.stem != "__init__":
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

        #with open("close_time.json")
        try:
            await self.db.close()
        except Exception:
            pass
        await super().logout()

def run():
    desc = """Streamio, the bot for all your streaming needs on discord
    Created by Chibli#0001"""

    loop = asyncio.get_event_loop()
    bot_params = {
        "prefix": ["!!","??"],
        "description": desc,
        "loop": loop
    }

    bot = Streamio(**bot_params)

    if var.TOKEN is None:
        logger.critical("Token is not set!")
        sys.exit(1)

    try:
        loop.run_until_complete(bot.start(var.TOKEN))
    except discord.LoginFailure:
        logger.critical("Invalid token")
        loop.run_until_complete(bot.logout())
    except KeyboardInterrupt:
        logger.warning("Bot was forcefully closed")
        loop.run_until_complete(bot.logout())
    finally:
        sys.exit(1)


if __name__ == "__main__":
    os.system("CLS")
    run()
