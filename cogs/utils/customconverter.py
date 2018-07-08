import datetime

from discord.ext import commands

class ToDatetime(commands.Converter):
    async def convert(self, ctx, date):
        format_string = f"%d{date[2]}%m"
        if len(date) == 5:
            date += f"{date[2]}{datetime.datetime.today().strftime('%y')}"

        if len(date) == 8:
            format_string += f"{date[5]}%y"
        elif len(date) == 10:
            format_string += f"{date[5]}%Y"

        try:
            return datetime.datetime.strptime(date, format_string)
        except ValueError:
            return None
