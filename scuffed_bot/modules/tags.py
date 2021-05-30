import discord.ext.commands as commands
import discord
from sqlalchemy.future import select
from sqlalchemy import delete, join
from scuffed_bot.database import Tag


class Tags(commands.Cog):
    def __init__(self, bot, db, logger):
        self.bot = bot
        self.db = db
        self.logger = logger

    async def get_tag(self, name, guild_id):
        async with self.db() as session:
            res = await session.execute(
                select(Tag).where(Tag.name == name and Tag.server_id == guild_id)
            )
            return res.scalars().first()

    async def get_tags(self, guild_id):
        async with self.db() as session:
            res = await session.execute(select(Tag).where(Tag.server_id == guild_id))
            return res.scalars().all()

    async def create_tag(self, name, content, guild_id):
        created = False
        if not await self.get_tag(name, guild_id):
            async with self.db() as session:
                async with session.begin():
                    session.add(Tag(name=name, content=content, server_id=guild_id))
            created = True
        return created

    async def remove_tag(self, name, guild_id):
        removed = False
        if await self.get_tag(name, guild_id):
            async with self.db() as session:
                async with session.begin():
                    await session.execute(
                        delete(Tag).where(
                            Tag.name == name and Tag.server_id == guild_id
                        )
                    )
            removed = True
        return removed

    # Tagging support
    @commands.command()
    async def tags(self, ctx):
        tags = await self.get_tags(ctx.guild.id)
        tag_list = f"This server has {len(tags)} tags\n"
        for tag in tags:
            tag_list += f"{tag.name}\n"
        await ctx.send(tag_list)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def tag(self, ctx):
        if not ctx.invoked_subcommand:
            msg_args = await util.parse_args(ctx.message.content, ['name'])
            tag = await self.get_tag(msg_args['name'], ctx.guild.id)
            if tag:
                await ctx.send(tag.content)
            else:
                await ctx.send(f"Tag {msg_args['name']} does not exist")

    @tag.group(pass_context=True, invoke_without_command=True)
    async def add(self, ctx):
        msg_args = await util.parse_args(ctx.message.content, ['name', 'content'])
        if not await self.get_tag(msg_args['name'], ctx.guild.id):
            await self.create_tag(msg_args['name'], msg_args['content'], ctx.guild.id)
            await ctx.send(f"Tag {msg_args['name']} created!")
        else:
            await ctx.send(f"Tag {msg_args['name']} already exists!")

    @tag.group(pass_context=True, invoke_without_command=True)
    async def remove(self, ctx):
        msg_args = await util.parse_args(ctx.message.content, ['name'])
        await self.remove_tag(msg_args['name'], ctx.guild.id)
        await ctx.send(f"Tag {msg_args['name']} was removed!")
