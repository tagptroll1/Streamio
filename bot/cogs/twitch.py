import discord
from discord.ext.commands import command, is_owner, has_permissions, Cog

class Twitch(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return str(ctx.channel.id) not in self.bot.blacklist

    @is_owner()
    @command()
    async def setstream(self, ctx, user:discord.Member):
        if isinstance(user.activity, discord.Streaming):
            title = f"{user.display_name} - {user.activity.name}"
            stream_url = user.activity.url
            stream_activity = discord.Streaming(
                name=title,
                url=stream_url
            )
            await self.bot.change_presence(activity=stream_activity)
            await ctx.send(f"Set my stream to {user.display_name}s!")
            return
        await ctx.send(f"{user.display_name} is not streaming..")

    @command()
    @has_permissions(administrator=True)
    async def shoutout(self, ctx, user:discord.Member):
        
        twitch_name, = await self.bot.db.fetchrow("""
            SELECT twitch_name FROM users
                WHERE guild_id = $1 AND id = $2;
        """, ctx.guild.id, user.id)

        if twitch_name is not "None":
            twitch_url = f"https://www.twitch.tv/{twitch_name}"
            embed = discord.Embed(title="Stream shoutout!")
            embed.description = (
                f"Make sure to follow {twitch_name}!\n"
                f"It would mean a lot to him, and everyone else\n"
                f"[Twitch.tv]({twitch_url})"
            )
            embed.colour = discord.Color.purple()
            await ctx.send(embed=embed)
            return
        await ctx.send( "I couldn't find a stream connected to this member!\n"
                       f"You can add a stream to my database by using {ctx.prefix}addstream @member twitchurl" )

    @command()
    async def addstream(self, ctx, member:discord.Member, url):
        twitch_name = url.replace("https://www.twitch.tv/", "")
        twitch_name = twitch_name.replace("www.twitch.tv/", "")

        if "/" in twitch_name:
            await ctx.send("Url doesn't seem correct, please give me a link formatted like this: https://www.twitch.tv/twitch_name")
            return

        await self.bot.db.execute("""
            UPDATE users
                SET twitch_name = $1
            WHERE guild_id = $2 AND id = $3
        """, twitch_name, ctx.guild.id, member.id)

        await ctx.send(f"Updated {member.display_name}s twitch info!")


def setup(bot):
    bot.add_cog(Twitch(bot))
