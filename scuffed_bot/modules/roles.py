import discord.ext.commands as commands
import discord
from sqlalchemy.future import select
from sqlalchemy import delete, join
from scuffed_bot.database import Role


class Roles(commands.Cog):
    def __init__(self, bot, db, logger):
        self.bot = bot
        self.db = db
        self.logger = logger

    async def get_role(self, name, guild_id):
        async with self.db() as session:
            res = await session.execute(
                select(Role).where(Role.name == name and Role.server_id == guild_id)
            )
            return res.scalars().first()

    async def get_roles(self, guild_id):
        async with self.db() as session:
            res = await session.execute(select(Role).where(Role.server_id == guild_id))
            return res.scalars().all()

    async def create_role(self, name, color, guild_id):
        created = False
        if not await self.get_role(name, guild_id):
            async with self.db() as session:
                async with session.begin():
                    session.add(Role(name=name, color=color, server_id=guild_id))
            created = True

        return created

    async def remove_role(self, name, guild_id):
        removed = False
        if await self.get_role(name, guild_id):
            async with self.db() as session:
                async with session.begin():
                    await session.execute(
                        delete(Role).where(
                            Role.name == name and Role.server_id == guild_id
                        )
                    )
            removed = True
        return removed

    @commands.command()
    async def roles(self, ctx, member: discord.Member = None):
        roles = ""
        role_list = await self.get_roles(self, ctx.guild.id)
        roles += f"This server has {len(role_list)} roles\n"
        for role in role_list:
            roles += f"{role}\n"
        await ctx.send(roles)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def role(self, ctx, member: discord.Member = None):
        pass

    @role.group(pass_context=True, invoke_without_command=True)
    async def add(self, ctx, member: discord.Member = None):
        _, _, role = ctx.message.content.split(" ")
        if len(role) == 2:
            name = role[0]
            color = role[1]
        elif len(role) == 2:
            name = role[0]
            color = None
        else:
            await ctx.send("Command needs to at least contain a role name")
            return
        res = await self.create_role(name, color, ctx.guild.id)
        if res:
            await ctx.send(f"{name} created")
        else:
            await ctx.send(f"{name} already exists")

    @role.group(pass_context=True, invoke_without_command=True)
    async def remove(self, ctx, member: discord.Member = None):
        _, role = ctx.message.content.split(" ")
        if await self.remove_role(role, ctx.guild.id):
            ctx.send(f"{role} removed")
        else:
            ctx.send(f"{role} does not exist")
