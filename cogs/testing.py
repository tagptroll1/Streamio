import discord
from discord.ext import commands

class Testing:
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def resetpresence(self, ctx):
        await self.bot.change_presence()

    @commands.is_owner()
    @commands.command()
    async def teststream(self, ctx):
        await self.bot.change_presence(activity=discord.Streaming(
            name="Teststream", url="https://www.twitch.tv/peebls"))

def setup(bot):
    bot.add_cog(Testing(bot))