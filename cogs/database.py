import discord
from discord.ext import commands
import asyncio
import asyncpg
import json
import textwrap
from collections import OrderedDict

from cogs.utils import db_queries as db_utils

class Database:
    def __init__(self, bot):
        self.bot = bot
        self.bot.db = None
        self.bot.loop.create_task(self.get_db_connection())


    async def __local_check(self, ctx):
        return str(ctx.channel.id) not in self.bot.blacklist

    async def get_db_connection(self):
        credentials = { "user": self.bot.secrets.DBUSER, 
                        "password": self.bot.secrets.DBPASS,
                        "database": "Streamio", "host": "127.0.01"}
        self.bot.db = await asyncpg.create_pool(**credentials)
        await self.create_tables()
        await self.check_members_in_db()
        await self.load_blacklist()
        await self.load_swearlist()
        await self.update_stuff()
        
    async def create_tables(self):
        if self.bot.db is None:
            await self.get_db_connection()

        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id bigint NOT NULL,
                guild_id bigint NOT NULL,
                level int,
                money bigint,
                pet_id int,
                twitch_name text,
                primary key(id, guild_id)
                );"""
            )

        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS blacklist(
                guild_id bigint NOT NULL,
                channel_id bigint NOT NULL,
                set_by bigint,
                date_set timestamp,
                primary key(guild_id, channel_id));"""
            )

        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS swearlist(
                guild_id bigint NOT NULL,
                channel_id bigint NOT NULL,
                set_by bigint,
                date_set timestamp,
                primary key(guild_id, channel_id));"""
            )

        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                msg_id bigint NOT NULL,
                author_id bigint NOT NULL,
                channel_id bigint,
                guild_id bigint,
                content bytea,
                date timestamp,
                primary key(msg_id, author_id));"""
            )

    async def check_members_in_db(self):
        for member in self.bot.get_all_members():
            try:
                await db_utils.create_user_account(
                    self.bot, member.id, member.guild.id)
            except Exception as e:
                print(e)

    async def load_blacklist(self):
        try:
            result = await self.bot.db.fetch("""
                SELECT * FROM blacklist""")
        except Exception as e:
            print(e)
            self.bot.logger.exception(e)

        for row in result:
            info = {
                "guild": row["guild_id"],
                "creator": row["set_by"],
                "date": row["date_set"],
                "channel": row["channel_id"]
            }
            self.bot.blacklist[str(row["channel_id"])] = info

    async def load_swearlist(self):
        try:
            result = await self.bot.db.fetch("""
                SELECT * FROM swearlist""")
        except Exception as e:
            print(e)
            self.bot.logger.exception(e)

        for row in result:
            info = {
                "guild": row["guild_id"],
                "creator": row["set_by"],
                "date": row["date_set"],
                "channel": row["channel_id"]
            }
            self.bot.swearlist[str(row["channel_id"])] = info

    async def update_stuff(self):
        """Updates values every 5 minutes"""
        while True:
            await asyncio.sleep(300)
            try:
                await self.bot.db.execute("""
                UPDATE users
                    SET money = money + 5;""")
                await db_utils.dump_log(self.bot)
            except Exception as e:
                self.bot.logger.error(e, exc_info=True)
            with open("swearjar.json", "w") as data:
                json.dump([self.bot.swearjar], data)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def money(self, ctx):
        money, = await self.bot.db.fetchrow("""
            SELECT money FROM users
            WHERE id = $1 AND guild_id = $2;""",
        ctx.author.id, ctx.guild.id)
        embed = discord.Embed(title=ctx.author.display_name)
        embed.colour = discord.Colour.green()
        embed.description = f"""
        You have ${money}!"""

        embed.set_footer(text="This menu is subject to change!",
                        icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="agive")
    @commands.has_permissions(administrator=True)
    async def admin_give_money(self, ctx, member:discord.Member, amount:int):
        if await db_utils.give_money(self.bot, amount, member.id, member.guild.id):
            await ctx.send(f"${amount} was given to {member.display_name}!",
                            delete_after=15)
        await ctx.message.delete()

    @commands.command(name="atake")
    @commands.has_permissions(administrator=True)
    async def admin_take_money(self, ctx, member:discord.Member, amount:int):
        if await db_utils.take_money(self.bot, amount, member.id, member.guild.id):
            await ctx.send(f"${amount} was taken from {member.display_name}!",
                           delete_after=15)
        await ctx.message.delete()

    @commands.command(name="aset")
    @commands.has_permissions(administrator=True)
    async def admin_set_money(self, ctx, member: discord.Member, amount: int):
        if await db_utils.set_money(self.bot, amount, member.id, member.guild.id):
            await ctx.send(f"${amount} was assigned to {member.display_name}!",
                           delete_after=15)
        await ctx.message.delete()

    @staticmethod
    def nick_money_format(record, guild):
        memb_id, money = record
        nick = f"{guild.get_member(memb_id).display_name}"
        money = f"${str(money)}"
        nick = nick[:20]
        return f"`{nick:<20}-{money:>15}`"

    async def show_leaderboard(self, ctx, top):
        if top > 50:
            await ctx.send("I can't display that many...")
            return
        elif top > len(ctx.guild.members):
            top = len(ctx.guild.members)
            title = f"Showing all in {ctx.guild.name}"
        else:
            title = f"Top {top} in {ctx.guild.name}"

        topx = await self.bot.db.fetch("""
            SELECT id, money FROM users
            WHERE guild_id = $1
            ORDER BY money desc
            limit $2;""", ctx.guild.id, top)

        embed = discord.Embed(title=title)
        
        leaderboard = "\n".join(
            [Database.nick_money_format(r, ctx.guild) for r in topx])
        embed.description = f"{leaderboard}"

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["leaderboards", "lidlboard", "top"])
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def leaderboard(self, ctx, top:int = 10):
        await self.show_leaderboard(ctx, top)

    @commands.command(name="top25")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def stop25(self, ctx):
        await self.show_leaderboard(ctx, 25)

    @commands.command(name="top10")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def top10(self, ctx):
        await self.show_leaderboard(ctx, 10)

    @commands.command(name="top5")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def top5(self, ctx):
        await self.show_leaderboard(ctx, 5)


    @commands.command(name="swearjar")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def swearjar(self, ctx):
        embed = discord.Embed(title="Swear jar")
        embed.description = textwrap.dedent(f"""
        💰 ${self.bot.swearjar}
        This is a jar full of $1 bills from everyone who have sworn
        in my presence.. This jar is shared among all servers.
        
        No... there are no ways of withdrawing this money!""")

        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Database(bot))
