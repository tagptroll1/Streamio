import asyncio
import textwrap
import json

import discord
from discord.ext import commands

from cogs.utils import db_queries as db_utils

class Events:
    def __init__(self, bot):
        self.bot = bot
        self.current_stream = None
        self.bad_words = self.load_bad_words()

    def word_check(self, msg):
        return any(word in msg.lower() for word in self.bad_words)

    def load_bad_words(self):
        with open("constants/badwords.json") as data:
            return json.load(data)

    async def on_connect(self):
        pass

    async def on_ready(self):
        pass

    async def on_resumed(self):
        pass

    async def on_typing(self, channel, user, when):
        pass

    async def on_message(self, message):
        if str(message.channel.id) in self.bot.blacklist:
            return
            
        if self.word_check(message.content):
            take = await db_utils.take_money(self.bot, 1, message.author.id, message.guild.id)
            
            if not take:
                await message.channel.send("Seems like you don't have $1 for the swearjar... I'll just delete the message")
                await message.delete()
                return
            prefix = await self.bot.get_prefix(message)
            embed = discord.Embed()
            embed.colour = discord.Color.red()
            embed.description = (
                f"Please don't swear {message.author.display_name}!\n"
                "$1 has been removed from your account and added to the swear jar!")
            embed.set_footer(text=f"use {prefix[0]}swearjar to see how much is in the swearjar!")
            await message.channel.send(embed=embed)
            self.bot.swearjar += 1
        #await self.bot.process_commands(message)

    async def on_message_delete(self, message):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_channel_create(self, channel):
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, b, a):
        # Activity changed
        if isinstance(a.activity, discord.Streaming):
            if isinstance(b.activity, discord.Streaming):
                # They were streaming, still streaming
                pass
            else:
                # They were NOT streaming before
                self.current_stream = a
                title = f"{a.display_name} - {a.activity.name}"
                stream_url = a.activity.url
                stream_activity = discord.Streaming(
                    name=title,
                    url=stream_url
                )
                await self.bot.change_presence(activity=stream_activity)
                if a.activity.twitch_name:
                    await self.bot.db.execute("""
                        UPDATE users
                            SET twitch_name = $1
                        WHERE guild_id = $2 AND id = $3
                    """, a.activity.twitch_name, a.guild.id, a.id)
        else:
            if isinstance(b.activity, discord.Streaming):
                # after is not streaming, before is
                if a is self.current_stream:
                    # Person who stopped was currently displayed
                    await self.bot.change_presence()
        
            

    async def on_guild_join(self, guild):
        pass

    async def on_guild_update(self, before, after):
        pass

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass

    async def on_guild_role_update(self, before, after):
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        pass

    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass   


def setup(bot):
    bot.add_cog(Events(bot))
