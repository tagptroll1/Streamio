import discord
from discord.ext import commands

class Twitch:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Twitch(bot))