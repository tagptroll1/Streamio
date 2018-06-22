import asyncio
import datetime

import discord
from discord.ext import commands
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

from cogs.utils import db_queries as db_utils
from cogs.utils.searchmodule import find_closest_records as close_str

class Moderation:
    """Commands that require administrator permissions"""

    def __init__(self, bot):
        self.bot = bot
        self.key = self.bot.secrets.ENCRYPT_KEY
        self.aes = AES.new(self.key, AES.MODE_ECB)

    async def __local_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.group(invoke_without_command=True)
    async def getlog(self, ctx):
        await ctx.send(embed=discord.Embed(
            description = ("Parent command for fetching logs, please use following sub command:\n\n"
                            "__time__ - Fetches by time starting at given, going back in time\n"
                            "__date__ - fetches by date\n"
                            "__author__ - fetches by author id\n"
                            "__channel__ - fetches by channel id\n"
                            "__guild__ - fetches by guild id\n"
                            "__content__ - attempt to search by content of msg\n\n"
                            "*__Please note you can only see logs from the same guild__*")
        ))

    @getlog.command()
    @commands.is_owner()
    async def secrets(self, ctx, limit=10, info=None):
        msg = None
        messages = await self.bot.db.fetch("""
            SELECT * FROM messages
                ORDER BY date desc
                LIMIT $1;""",
            limit)

        embed = discord.Embed(
            title=f"{limit} last messages from everything")
        desc = ""
        for msg in messages:
            msgid, authorid, channelid, guildid, content, date = msg
            if authorid == self.bot.user.id:
                continue

            guild = None
            channel = None
            msg = None
            member = None

            try:
                guild = self.bot.get_guild(guildid)
                channel = guild.get_channel(channelid)
                msg = await channel.get_message(msgid)
                member = guild.get_member(authorid)
            except Exception:
                pass

            form_date = date.strftime("%d/%m/%y %H:%M")

            if guild and channel and member and msg and not info:
                desc += f"{form_date} in {guild.name} #{channel.name} @{member.display_name}: \n\t\"{msg.content}\"\n"
                continue

            elif guild and channel and member and msg:
                desc += f"{form_date}: {msg.content}\n"
                continue

            if content:
                msg = self.aes.decrypt(content)
                msg = Padding.unpad(msg, 16).decode("utf-8")
                desc += f"{form_date}: {msg}\n"
            

        embed.description = f"```{desc[:2000]}```"

        if msg:
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=discord.Embed(description="No logs available"))

    @getlog.command()
    async def author(self, ctx, member: discord.Member, limit: int=10):
        query = """
            SELECT * FROM messages
                WHERE author_id = $1 AND guild_id = $2
            ORDER BY date desc
            LIMIT $3;"""
        rows = await db_utils.get_messages(
            self.bot, ctx, query, member.id, ctx.guild.id, limit)

        embed = discord.Embed(
            title=f"{limit} last messages from {member.display_name}")
        desc = ""
        for msg in rows:
            msg, author, channel, guild, content, date = msg

            if date and channel and content:
                desc += f"{date} #{channel.name}: {content}\n" 
            elif date and content:
                desc += f"{date}: {content}\n"
            else:
                desc += f"{content}\n"

        embed.description = f"```{desc[:2000]}```"

        if rows:
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=discord.Embed(description="No logs available"))
        
    @getlog.command()
    async def channel(self, ctx, channel:discord.TextChannel, limit:int=10):
        query = """
            SELECT * FROM messages
                WHERE channel_id = $1 AND guild_id = $2
            ORDER BY date desc
            LIMIT $3;"""
        rows = await db_utils.get_messages(
            self.bot, ctx, query, ctx.channel.id, ctx.guild.id, limit)

        embed = discord.Embed(
            title=f"{limit} last messages from {channel.name}")
        desc = ""
        for msg in rows:
            msg, author, channel, guild, content, date = msg

            if date and author and content:
                desc += f"{date} {author.display_name}: {content}\n"
            elif date and content:
                desc += f"{date}: {content}\n"
            else:
                desc += f"{content}\n"

        embed.description = f"```{desc[:2000]}```"

        if rows:
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=discord.Embed(description="No logs available"))

    @getlog.command()
    async def content(self, ctx, content, limit: int=10):
        query = """
            SELECT * FROM messages
                WHERE guild_id = $1
            ORDER BY date desc
            LIMIT 1000;"""
        rows = await self.bot.db.fetch(
            query, ctx.guild.id)

        embed = discord.Embed(
            title=f"Fetched logs resembling search query")
        desc = ""


        topx = close_str(content, rows, limit)
        for _, record in reversed(topx):
            msgid, authorid, channelid, _, content, date = record
            date = date.strftime("%d/%m/%y %H:%M")
            msg = None
            try:
                msg = ctx.guild.get_message(msgid)
            except Exception:
                pass

            channel = ""
            try:
                channel = ctx.guild.get_channel(channelid).name
            except Exception:
                pass

            author = ""
            try:
                author = ctx.guild.get_member(authorid).mention
            except Exception:
                pass

            if msg:
                content = msg.content
            else:
                aes = AES.new(self.bot.secrets.ENCRYPT_KEY, AES.MODE_ECB)
                content = aes.decrypt(content)
                content = Padding.unpad(content, 16).decode("utf-8")

            prefix = f"{date} {author} #{channel}:"
            if len(prefix) > 25: 
                prefix = prefix[:70]
                prefix += "\n"
            prefix = f"__**{prefix}**__"
            desc += f"{prefix}*{content}*\n"

        embed.description = f"{desc[:2000]}"

        if rows:
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=discord.Embed(description="No logs available"))

    @getlog.command()
    async def guild(self, ctx, limit: int=10):
        query = """
            SELECT * FROM messages
                WHERE guild_id = $1
            ORDER BY date desc
            LIMIT $2;"""
        rows = await db_utils.get_messages(
            self.bot, ctx, query, ctx.guild.id, limit)

        embed = discord.Embed(
            title=f"{limit} last messages from {ctx.guild.name}")
        desc = ""
        for msg in rows:
            msg, author, channel, guild, content, date = msg

            if date and channel and author and content:
                desc += f"{date} #{channel.name} {author.display_name}: {content}\n"
            elif date and channel and content:
                desc += f"{date} #{channel.name}: {content}\n"
            elif content and channel:
                desc += f"#{channel.name}: {content}\n"
            else:
                desc += f"{content}\n"


        embed.description = f"```{desc[:2000]}```"

        if rows:
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=discord.Embed(description="No logs available"))

    @commands.group(invoke_without_command=True)
    async def swearfilter(self, ctx):
        pass

    @swearfilter.command(name="add")
    async def add_swearfilter(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel
        self.bot.swearlist[str(channel.id)] = {
            "guild": ctx.guild.id,
            "creator": ctx.author.id,
            "date": datetime.datetime.utcnow(),
            "channel": channel.id
        }

        await self.bot.db.execute("""
            INSERT INTO swearlist
                (guild_id, channel_id, set_by, date_set)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, channel_id)
            DO NOTHING;
        """, ctx.guild.id, channel.id, ctx.author.id, datetime.datetime.utcnow())
        await ctx.send(f"My swearing filter has been activated for #{channel.name}")

    @swearfilter.command(name="remove")
    async def remove_swearfilter(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel
        try:
            del self.bot.swearlist[str(channel.id)]
        except Exception as e:
            await ctx.send(e)
            return

        await self.bot.db.execute("""
            DELETE FROM swearlist
            WHERE guild_id = $1 AND channel_id = $2;
        """, ctx.guild.id, channel.id)

        await ctx.send(f"My swearing filter has been de-activated for #{channel.name}")

    @commands.group(invoke_without_command=True)  # TODO add this
    async def blacklist(self, ctx, limit=10):
        pass

    @blacklist.command(name="add")
    async def add_blacklist(self, ctx, channel:discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        self.bot.blacklist[str(channel.id)] = {
            "guild": ctx.guild.id,
            "creator": ctx.author.id,
            "date": datetime.datetime.utcnow(),
            "channel": channel.id
        }

        await self.bot.db.execute("""
            INSERT INTO blacklist
                (guild_id, channel_id, set_by, date_set)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, channel_id)
            DO NOTHING;
        """, ctx.guild.id, channel.id, ctx.author.id, datetime.datetime.utcnow())

        await ctx.send(f"The channel {channel.name} has been blacklisted! My commands and features wont work there now")

    @blacklist.command(name="remove")
    async def remove_blacklist(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        try:
            del self.bot.blacklist[str(channel.id)]
        except Exception as e:
            await ctx.send(e)
            return 
            
        await self.bot.db.execute("""
            DELETE FROM blacklist
            WHERE guild_id = $1 AND channel_id = $2;
        """, ctx.guild.id, channel.id)

        await ctx.send(f"The channel {channel.name} has been unblocked! My commands and features will work there now")

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
