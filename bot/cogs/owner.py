import asyncio

import discord
from discord.ext.commands import command, Cog

class Owner(Cog):
    """Owner of bot only commands"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @command(name="loadcog", aliases=["load"])
    async def load_cog(self, ctx, cog):
        if not "cogs." in cog:
            cog = "cogs." + cog
        try:
            self.bot.load_extension(cog)
            await ctx.send(f"loaded {cog}")
        except (discord.ClientException | ImportError) as e:
            await ctx.send(f"Something went wrong loading {cog}!")
            await ctx.send(f"```{e}```")

    @command(name="unloadcog", aliases=["unload"])
    async def unload_cog(self, ctx, cog):
        if not "cogs." in cog:
            cog = "cogs." + cog
        try:
            self.bot.unload_extension(cog)
            await ctx.send(f"Unloaded {cog}")
        except (discord.ClientException | ImportError) as e:
            await ctx.send(f"Something went wrong unloading {cog}!")
            await ctx.send(f"```{e}```")

    @command(name="cogs")
    async def get_cogs(self, ctx):
        await ctx.send(", ".join(list(self.bot.cogs)))

    @command()
    async def shutdown(self, ctx):
        await ctx.send("Bye :(")
        self.bot.logger.info("Bot was shutdown by command shutdown")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
