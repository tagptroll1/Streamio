import re
import asyncio
import inspect
import datetime as dt

import discord
from discord.ext.commands import command, guild_only, Cog

class Utils(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @guild_only()
    async def remind_me(self, ctx, time, *, message=None):
        """remind_me <time> [message]
        
        Time units:
            d - days
            h - hours
            m - minutes
            s - seconds

            syntax: <number><timeunit>
            examples:
            remind_me 20m55s do stuff
            remind_me 1d20s do stuff tomorrow
            remind_me 2d10h23m55s very specificly in this time

        """
        await ctx.message.delete()
        if message is None:
            message = "No message attached!"
        pattern = re.compile(
            r'((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?')

        match = pattern.fullmatch(time)
        if match:
            kwargs = {
                "days": int(match.group("days")) if match.group("days") is not None else 0,
                "hours": int(match.group("hours")) if match.group("hours") is not None else 0,
                "minutes": int(match.group("minutes")) if match.group("minutes") is not None else 0,
                "seconds": int(match.group("seconds")) if match.group("seconds") is not None else 0,
            }
        else:
            return
        reminder_string = ""
        reminder_string += f'{kwargs["days"]:g} days ' if kwargs.get(
            "days") else ""
        reminder_string += f'{kwargs["hours"]:g} hours ' if kwargs.get(
            "hours") else ""
        reminder_string += f'{kwargs["minutes"]:g} minutes ' if kwargs.get(
            "minutes") else ""
        reminder_string += f'{kwargs["seconds"]:g} seconds ' if kwargs.get(
            "seconds") else ""
        await ctx.send(f"""A reminder for {reminder_string}has been set\n
                        \r__Message:__
                        \r{message}""", delete_after=10)

        delta = dt.timedelta(**kwargs)
        sleeptime = delta.total_seconds()
        await asyncio.sleep(sleeptime)

        await ctx.send(f"It's been {sleeptime:g} seconds since "
                       f"{ctx.author.mention} made this reminder:\n{message}")


def setup(bot):
    bot.add_cog(Utils(bot))
