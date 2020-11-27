import random
import asyncio
import textwrap

import discord
from discord.ext.commands import command, cooldown, group, BucketType, Cog

from bot.cogs.utils import db_queries as db_utils

class Games(Cog):

    response_form = {
        "choose": "I choose",
        "choice": "I choose",
        "select": "I selected",
        "pick": "I picked"
    }

    def __init__(self, bot):
        self.bot = bot
    
    async def __local_check(self, ctx):
        return str(ctx.channel.id) not in self.bot.blacklist

    async def bet_check(self, bet, ctx):
        money, = await self.bot.db.fetchrow("""
            SELECT money FROM users
            WHERE id = $1 AND guild_id = $2;""",
        ctx.author.id, ctx.guild.id)

        if money < bet or money == 0:
            await ctx.send(f"You don't have enough money!", delete_after=10)
            return False

        if bet < 0:
            await ctx.send("You can't bet with negative numbers..", delete_after=10)
            return False
        return True


    @command()
    async def test(self, ctx, cont):
        try:
            await ctx.send(self.bot.__dict__.get(cont))
        except Exception as e:
            await ctx.send(f"```{e}```") 

    @command(aliases=["roll", "rolldice"])
    async def dice(self, ctx, max:int=6):
        await ctx.send(f"Dice says.. {random.randint(0, max)}") 

    @group(name="choose", aliases=["choice", "select", "pick"])
    async def choose_random(self, ctx, *options):
        ctx.response_form = Games.response_form.get(ctx.invoked_with)
        await ctx.send(f"{ctx.response_form}.. {random.choice(options)}!")
            
    @command(aliases=["chooseuser", "chooseperson", "chooseguy"])
    async def choose_member(self, ctx):
        online = [x for x in ctx.channel.members if x.status != discord.Status.offline]
        await ctx.send(f"I chose.. {random.choice(online).display_name}")

    @command(aliases=["role", "fromrole"])
    async def member_from(self, ctx, role:discord.Role):
        await ctx.send(f"I chose.. {random.choice(role.members).display_name}")

    @command()
    @cooldown(1, 1, BucketType.channel)
    async def guessdice(self, ctx, guess:int, bet:int):
        if not await self.bet_check(bet, ctx):
            return

        if guess not in range(1,7):
            await ctx.send("A dice only has 6 sides... doofus", delete_after=10)
            return

        roll = random.randint(1,6)
        won = True if roll == guess else False

        if won:
            win_msg = f"""Congrats! You guessed the roll {roll} you won ${4*bet}!"""
            if await db_utils.give_money(self.bot, 4*bet, ctx.author.id, ctx.guild.id):
                await ctx.send(win_msg)
            else:
                await ctx.send("Db didn't return True for give_money")
        else:
            lose_msg = f"""You guessed {guess} the roll was {roll}, you lose ${bet}!"""
            if await db_utils.take_money(self.bot, bet, ctx.author.id, ctx.guild.id):
                await ctx.send(lose_msg)
            else:
                await ctx.send("Db didn't return True for take_money")


    async def roulette(self, ctx, bet):
        win = True if random.randint(0, 100) < 50 else False
        if win:
            win_msg = f"""You win the 50/50! You won ${bet*2}"""
            await db_utils.give_money(self.bot, bet, ctx.author.id, ctx.guild.id)
            await ctx.send(win_msg)
        else:
            lose_msg = f"""You lost the 50/50! ${bet} was lost"""
            await db_utils.take_money(self.bot, bet, ctx.author.id, ctx.guild.id)
            await ctx.send(lose_msg)

    @group(name="rng", aliases=["50/50", "5050", "50", "roulette"],
                    invoke_without_command=True)
    @cooldown(1, 1, BucketType.channel)
    async def rng_50_50_game(self,ctx, bet:int):
        if await self.bet_check(bet, ctx):
            await self.roulette(ctx, bet)
        

    @rng_50_50_game.command(name="all")
    @cooldown(1, 1, BucketType.channel)
    async def roulette_all(self, ctx):
        money, = await self.bot.db.fetchrow("""
            SELECT money FROM users
            WHERE id = $1 AND guild_id = $2;""",
            ctx.author.id, ctx.guild.id)

        if await self.bet_check(money, ctx):
            await self.roulette(ctx, money)


    @command(name="duel")
    @cooldown(1, 1, BucketType.channel)
    async def duel_someone(self, ctx, other:discord.Member, bet:int):
        if other is ctx.author or other.bot:
            await ctx.send("You can't duel this person!")
            return

        msg_text = (f"{ctx.author.display_name} has challenged {other.mention} to a duel!\n"
                    f"Do you accept {other.display_name}? yes/no ")
        f1 = await ctx.send(msg_text)
        await ctx.message.delete()

        def check(m):
            if m.author != other:
                return False
            if m.content.lower() not in ("yes", "ye", "y", "yea", "accept",
                                        "no", "n", "nah", "decline"):
                return False
            return True
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return
        finally:
            await f1.edit(content=f"~~{msg_text}~~\nNo response... Canceling..")

        if msg.content.lower() in ("no", "n", "nah", "decline"):
            await ctx.send("Duel canceled!", delete_after=10)
            return
        row = await self.bot.db.fetch("""
            SELECT id, money FROM users
            WHERE guild_id = $1 
            AND (id = $2 OR id = $3);""",
            ctx.guild.id, ctx.author.id, other.id)

        author = next(r for r in row if r["id"] == ctx.author.id)
        other = next(r for r in row if r["id"] == other.id)

        author_m = ctx.guild.get_member(author["id"])
        other_m = ctx.guild.get_member(other["id"])

        if author["money"] < bet:
            await ctx.send("You don't have enough money!")
            return

        elif other["money"] < bet:
            await ctx.send(
                f"{other_m.display_name} doesn't have enough money to accept!")
            return

        elif bet < 0:
            await ctx.send("You can't bet with negative numbers..", delete_after = 10)
            return

        author_win = True if random.choice([0, 1]) else False

        if author_win:
            await ctx.send(
                f"{author_m.display_name} has defeated {other_m.display_name}!\n"\
                f"${bet} has been transfered from {other_m.display_name} to {author_m.display_name}")
            await db_utils.transfer_money(self.bot, bet, other_m.id, author_m.id, ctx.guild.id)
            winner = author_m
            

        else:
            await ctx.send(
                f"{other_m.display_name} has defeated {author_m.display_name}!\n"\
                f"${bet} has been transfered from {author_m.display_name} to {other_m.display_name}")
            await db_utils.transfer_money(self.bot, bet, author_m.id, other_m.id, ctx.guild.id)
            winner = other_m

        def check2(m):
            return m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check2, timeout=10)
        except asyncio.TimeoutError:
            return

        if msg.content in ("lol", "rekt", "ez") and msg.author == winner:
            await ctx.send("Toxic behavior detected! I'll take half of your winnings!")
            await db_utils.take_money(self.bot, bet/2, winner.id, ctx.guild.id)

    @command(aliases=["fibo"])
    async def fibonacci(self, ctx, cycles:int):
        if cycles > 15000 or cycles < 1:
            await ctx.send("Too big/small number!")
            
        fibs = [0, 1]
        for _ in range(2, cycles+1):
            fibs.append(fibs[-1] + fibs[-2])

        if cycles < 9500:
            await ctx.send(fibs[-1])
        else:
            await ctx.send(str(fibs[-1])[:2000])
            await ctx.send(str(fibs[-1])[2000:])
        
def setup(bot):
    bot.add_cog(Games(bot))
