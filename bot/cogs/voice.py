import discord
from discord.ext.commands import Cog

class Voice(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return str(ctx.channel.id) not in self.bot.blacklist

def setup(bot):
    bot.add_cog(Voice(bot))
