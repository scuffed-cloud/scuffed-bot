import discord.ext.commands as commands
import discord
from sqlalchemy.future import select
from scuffed_bot.database import Server, Tag
import traceback


class Base(commands.Cog):
    def __init__(self, bot, db, logger):
        self.bot = bot
        self.db = db
        self.logger = logger

    async def create_guild(self, guild):
        async with self.db() as session:
            res = await session.execute(select(Server).where(Server.id == guild.id))
        async with self.db() as session:
            if not res.scalars().first():
                async with session.begin():
                    session.add(Server(id=guild.id))
                    await session.commit()
                    self.logger.info(f"Guild {guild.id}:{guild.name} on-boarded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry, you lack the permissions to do that")
        # this ignores messages that are like "$500 is what I paid"
        elif isinstance(error, commands.errors.CommandNotFound):
            pass
        else:
            self.logger.error(f"Error reported: {error}")
            await ctx.send("Uh oh, some uknown error occured and was logged")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.create_guild(guild)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")
