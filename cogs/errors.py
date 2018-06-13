import discord
from discord.ext import commands

class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.

        ctx   : Context
        error : Exception
        """
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        self.bot.logger.error(error)

        if isinstance(error, commands.MissingRequiredArgument):
            """Exception raised when parsing a command and a parameter 
            that is required is not encountered.
            """
            print(error)

        elif isinstance(error, commands.BadArgument):
            """Exception raised when a parsing or conversion failure is 
            encountered on an argument to pass into a command.
            """
            print(error)

        elif isinstance(error, commands.NoPrivateMessage):
            """Exception raised when an operation does not work in private message contexts."""
            print(error)

        elif isinstance(error, commands.NotOwner):
            """Exception raised when the message author is not the owner of the bot."""
            print(error)

        elif isinstance(error, commands.MissingPermissions):
            """Exception raised when the command invoker lacks permissions to run command."""
            await ctx.send(error)

        elif isinstance(error, commands.BotMissingPermissions):
            """Exception raised when the bot lacks permissions to run command."""
            await ctx.send(error)

        elif isinstance(error, commands.CommandOnCooldown):
            """Exception raised when the command being invoked is on cooldown."""
            print(error)

        elif isinstance(error, commands.CheckFailure):
            """Exception raised when the predicates in Command.checks have failed."""
            print(error)

        elif isinstance(error, commands.DisabledCommand):
            """Exception raised when the command being invoked is disabled."""
            print(error)

        elif isinstance(error, commands.CommandInvokeError):
            """Exception raised when the command being invoked raised an exception."""
            print(error)

        elif isinstance(error, commands.TooManyArguments):
            """Exception raised when the command was passed too many arguments 
            and its Command.ignore_extra attribute was not set to True.
            """
            print(error)
        elif isinstance(error, commands.CommandError):
            """The base exception type for all command related errors.

            This inherits from discord.DiscordException.
            This exception and exceptions derived from it are handled in a 
            special way as they are caught and passed into a 
            special event from Bot, on_command_error().
            """
            print(error)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
