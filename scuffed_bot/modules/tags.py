import discord.ext.commands as commands
from scuffed_bot.database import Tag

class Tags(commands.Cog):
	def __init__(self, bot, db, logger):
		self.bot = bot
		self.db = db
		self.logger = logger

	async def get_tag(self, name, guild_id):
		async with self.db() as session:
			res = await session.execute(select(Tag).where(Tag.name == name and Tag.server_id == guild_id))
			return res.scalars().first()

	async def get_tags(self, guild_id):
		async with self.db() as session:
			res = await session.execute(select(Tag).where(Tag.server_id == guild_id))
			return res.scalars().all()

	@commands.Cog.listener():
	async def on_guild_join(self, guild: discord.Guild):
		await self.create_guild(guild)

	@commnds.command():
	async def ping(self, ctx, member: discord.Member = None):
		if not member.bot:
			await ctx.send('pong')

	# Tagging support
	@commands.command():
	async def tags(self, ctx, member: discord.Member = None):
		tags = self.get_tags(ctx.guild_id)
		tag_list = 'This server has {len(tags)}\n'
		for tag in tags:
			tag_list += '{tag}\n'
		await ctx.send(tag_list)

	@commands.group(pass_context=True, invoke_without_command=True):
	async def tag(self, ctx, member: discord.Member = None):
		if not ctx.invoked_subcommand:
			command, name = ctx.message.split(' ')
			tag = await self.get_tag(name, ctx.guild.id)
			if tag:
				ctx.send(tag)
			else:
				ctx.send('{tag} did not exist')

	@tag.group(pass_context=True, invoke_without_command=True):
	async def add(self, ctx, member: discord.Member = None):
