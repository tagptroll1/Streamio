import json
import asyncio
import textwrap
import datetime

import discord
from discord.ext import commands
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

from cogs.utils import db_queries as db_utils


class Events:
    def __init__(self, bot):
        self.bot = bot
        self.current_stream = None
        self.key = self.bot.secrets.ENCRYPT_KEY
        self.aes = AES.new(self.key, AES.MODE_ECB)
        self.bad_words = self.load_bad_words()
        self.money_cooldown = commands.CooldownMapping.from_cooldown(
                            1.0, 60.0, commands.BucketType.user)
        self.swear_cooldown = commands.CooldownMapping.from_cooldown(
                            1.0, 15.0, commands.BucketType.user)


    def word_check(self, msg):
        return any(word in msg.lower() for word in self.bad_words)

    def load_bad_words(self):
        with open("constants/badwords.json") as data:
            return json.load(data)

    async def log_message(self, msg):
        msg_cont = f"{msg.content}"
        for attach in msg.attachments:
            msg_cont += f" - {attach.url}"

        if not msg_cont:
            msg_cont = "<Attachement not saved>"
        b_reason = Padding.pad(bytes(msg_cont, "utf-8"), 16)
        encrypted_msg = self.aes.encrypt(b_reason)

        date = datetime.datetime.utcnow()

        self.bot.msg_log.append({
            "id": msg.id,
            "author": msg.author.id,
            "channel": msg.channel.id,
            "guild": msg.guild.id,
            "msg": encrypted_msg,
            "date": date
        })
        

    async def on_connect(self):
        pass

    async def on_ready(self):
        pass

    async def on_resumed(self):
        pass

    async def on_typing(self, channel, user, when):
        pass

    async def on_message(self, message):
        if message.author.bot:
            return
            
        await self.log_message(message)

        bucket = self.money_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if not retry_after:
            await db_utils.give_money(self.bot, 1, message.author.id, message.guild.id)


        if str(message.channel.id) in self.bot.blacklist:
            return
        
        if str(message.channel.id) in self.bot.swearlist:
            if self.word_check(message.content):
                take = await db_utils.take_money(self.bot, 1, message.author.id, message.guild.id)
                
                if not take:
                    await message.channel.send(
                        discord.Embed(descritpion=
                        "Seems like you don't have $1 for the swearjar... I'll just delete the message"))
                    await message.delete()
                    return
                embed = discord.Embed()
                embed.colour = discord.Color.red()
                embed.description = (
                    f"Please don't swear {message.author.display_name}!\n Took $1 off your account!")
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
        pass
        
            

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
