import discord.ext.commands as commands
import discord
from sqlalchemy.future import select
from scuffed_bot.database import Server, Tag


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
        self.logger.error(f"Error reported: {error}")
        await self.ctx.send("Uh oh, some error occured and was logged")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.create_guild(guild)
