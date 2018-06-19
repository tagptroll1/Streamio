import textwrap
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands

class Info:
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(aliases=["invitelink", "invite", "link"])
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def invite_link(self, ctx):
        link = self.bot.invite_link
        embed = discord.Embed(title="Invite me!", url=link)
        embed.colour = discord.Color.purple()
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def info(self, ctx):
        guild = ctx.guild
        owner = self.bot.app_info.owner
        bot   = self.bot

        embed = discord.Embed(title="Information")
        embed.colour = discord.Color.purple()
        if ctx.guild:
            embed.add_field(name="__Guild__", value = textwrap.dedent(f"""
                **Id** 
                {guild.id}
                **Name:** 
                {guild.name}
                **Owner** 
                {guild.owner.mention}
                **Members:** {guild.member_count}
                **Region:** {guild.region}
                **Created:** {datetime.strftime(guild.created_at, '%d.%m.%Y')}
                """)
            )
        else:
            embed.add_field(name="Msg Author", value=textwrap.dedent(f"""
                **Id** 
                {ctx.author.id}
                **Name** 
                {str(ctx.author)}
                {ctx.author.mention}
                Soon more to be added
                """)
            )
        embed.add_field(name="__Bot Owner__", value=textwrap.dedent(f"""
            **Id** 
            {owner.id}
            **Name** 
            {str(owner)}
            {owner.mention}
            Soon more to be added
            """)
        )
        embed.add_field(name="__Bot__", value=textwrap.dedent(f"""
            **Id** 
            {bot.user.id}
            **Name** 
            {str(bot.user)}
            {bot.user.mention}
            **Commands:** {len(bot.commands)}
            **Guilds:** {len(bot.guilds)}
            **Members:** {len(set(bot.get_all_members()))}
            Soon more to be added
            """)
        )

        await ctx.send(embed=embed)

    @info.command()
    async def member(self, ctx, member:discord.Member):
        joined = datetime.strftime(member.joined_at, '%d.%m.%Y')
        now = datetime.utcnow()
        difference = now - member.joined_at

        embed = discord.Embed(title=str(member))
        embed.colour = discord.Color.purple()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="__Info__", value=textwrap.dedent(f"""
            **Id**
            {member.id}
            **Name**
            {member.name}
            **Nick**
            {member.mention}
            **Top_role:** 
            {member.top_role.name}
            **Bot:** {"Yes" if member.bot else "No"}
            **Joined:** {joined}
            **Member for** {difference.days} days
            Soon more to be added
            """)
        )
        await ctx.send(embed=embed)

    @commands.guild_only()
    @info.command()
    async def role(self, ctx, role:discord.Role):
        created = datetime.strftime(role.created_at, "%d.%m.%Y")

        embed = discord.Embed(title=str(role))
        embed.colour = discord.Color.purple()
        embed.add_field(name="Info", value=textwrap.dedent(f"""
            **Id**
            {role.id}
            **Name**
            {role.name}
            **Guild**
            {role.guild}
            **Hoist:** {"Yes" if role.hoist else "No"}
            **Mentionable:** {"Yes" if role.mentionable else "No"}
            **Created at:** {created}
            """)
        )

        if len(role.members) < 25:
            members = [mem.mention for mem in role.members]
            embed.add_field(name="Members", value="\n".join(members))

        perms = [perm.title().replace("_", " ") for perm, value in role.permissions if value]

        embed.add_field(name="Permissions", value="\n".join(perms))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def guilds(self, ctx):
        embed = discord.Embed(title="All my guilds")
        guilds = [f"{guild.name}, members: {len(guild.members)}" for guild in self.bot.guilds]
        embed.description = "\n".join(guilds)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
