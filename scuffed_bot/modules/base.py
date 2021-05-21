import discord.ext.commands as commands
from scuffed_bot.database import Server, Tag

class Base(commands.Cog):

	def __init__(self, bot, db, logger):
		self.bot = bot
		self.db = db
		self.logger = logger

	async def create_guild(self, guild):
		async with self.db() as session:
			res = await session.execute(select(Server).where(Server.id == guild.id))
			if res.scalars().first():
				async with session.begin():
					session.add(Server(id=guild.id))
					await session.commit()

	@commands.Cog.listener():
	async def on_guild_join(self, guild: discord.Guild):
		await self.create_guild(guild)
