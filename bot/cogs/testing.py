import discord
from discord.ext.commands import command, is_owner, Cog

class Testing(Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_owner()
    @command()
    async def resetpresence(self, ctx):
        await self.bot.change_presence()

    @is_owner()
    @command()
    async def teststream(self, ctx):
        await self.bot.change_presence(
            activity=discord.Streaming(
                name="Teststream",
                url="https://www.twitch.tv/peebls"
            )
        )

def setup(bot):
    bot.add_cog(Testing(bot))