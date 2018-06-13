import asyncio

import discord
from discord.ext import commands

class Moderation:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def kick(self, ctx, tokick: discord.Member, *, reason=None):
        """Kick a member from the guild
        
        member - to kick
        reason - defaults to None
        """
        try:
            await tokick.kick(reason=reason)
            await ctx.send(f"{tokick.display_name} has been kicked! Reason: {reason}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong kicking {tokick.display_name}")
            await ctx.send(f"```{e}```")

    @commands.command()
    async def ban(self, ctx, toban: discord.Member, *, reason=None):
        """Bans a member from the guild, deletes 1 day old messages
        
        member - to banned
        reason - defaults to None
        """
        try:
            await toban.ban(reason=reason)
            await ctx.send(f"{toban.display_name} has been banned! Reason: {reason}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong banning {toban.display_name}")
            await ctx.send(f"```{e}```")

    @commands.command(name="nickname", aliases=["nick", "name", "username"])
    async def edit_nickname(self, ctx, toedit: discord.Member, *, new_name):
        """Edits a member from the guilds nickname
        
        member - to change nickname
        newname - new nickname for member
        """
        old_name = toedit.display_name
        try:
            await toedit.edit(nick=new_name)
            await ctx.send(f"Edited {old_name} to {new_name}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong changing {toedit.display_name}s nickname")
            await ctx.send(f"```{e}```")

    @commands.command(name="mute")
    async def mute(self, ctx, tomute: discord.Member, *, reason=None):
        """Mutes a member from the guild
        
        member - to mute
        reason - defaults to None
        """
        try:
            await tomute.edit(mute=True, reason=reason)
            await ctx.send(f"{tomute.display_name} has been muted!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong muting {tomute.display_name}")
            await ctx.send(f"```{e}```")

    @commands.command(name="unmute")
    async def unmute(self, ctx, tounmute: discord.Member, *, reason=None):
        """Unmutes a member from the guild
        
        member - to unmute
        reason - defaults to None
        """
        try:
            await tounmute.edit(mute=False, reason=reason)
            await ctx.send(f"{tounmute.display_name} has been unmuted!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong unmuting {tounmute.display_name}")
            await ctx.send(f"```{e}```")

    @commands.command(name="deafen")
    async def deafen(self, ctx, todeafen: discord.Member, *, reason=None):
        """Deafen a member from the guild

        member - to deafen
        reason - defaults to None
        """
        try:
            await todeafen.edit(deafen=True, reason=reason)
            await ctx.send(f"{todeafen.display_name} has been deafened!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong deafening {todeafen.display_name}")
            await ctx.send(f"```{e}```")

    @commands.command(name="undeafen")
    async def undeafen(self, ctx, toundeafen: discord.Member, *, reason=None):
        """Undeafen a member from the guild
        
        member - to undeafen
        reason - defaults to None
        """
        try:
            await toundeafen.edit(deafen=False, reason=reason)
            await ctx.send(f"{toundeafen.display_name} has been undeafened!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong undeafening {toundeafen.display_name}")
            await ctx.send(f"```{e}```")


def setup(bot):
    bot.add_cog(Moderation(bot))
