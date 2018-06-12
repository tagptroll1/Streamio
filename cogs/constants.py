from pathlib import Path

import discord
from discord.ext import commands

def setup(bot):
    bot.location = Path(".")
    bot.cogs_location = Path("./cogs")
    bot.resources = Path("./resources")
    #bot.db = db
    bot.logger.info("Constants loaded.")