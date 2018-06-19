from pathlib import Path

import discord
from discord.ext import commands

def setup(bot):
    bot.invite_link="https://discordapp.com/oauth2/authorize?client_id=455941658195001346&scope=bot"
    bot.location = Path(".")
    bot.cogs_location = Path("./cogs")
    bot.resources = Path("./resources")
    #bot.db = db
    bot.logger.info("Constants loaded.")
    
