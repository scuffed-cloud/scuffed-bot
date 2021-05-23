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

    async def create_role(self, name, color, guild_id, role_id):
        created = False
        if not await self.get_role(name, guild_id):
            async with self.db() as session:
                async with session.begin():
                    session.add(
                        Role(name=name, color=color, server_id=guild_id, id=role_id)
                    )
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
    async def roles(self, ctx):
        roles = ""
        role_list = await self.get_roles(ctx.guild.id)
        roles += f"This server has {len(role_list)} roles\n"
        for role in role_list:
            roles += f"{role.name}\n"
        await ctx.send(roles)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def role(self, ctx):
        pass

    @role.group(pass_context=True, invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx):
        cmd = ctx.message.content.split(" ")
        if len(cmd) == 4:
            name = cmd[2]
            color = int(cmd[3])
        elif len(cmd) == 3:
            name = cmd[2]
            color = None
        else:
            await ctx.send("Command needs to at least contain a role name")
            return
        if color:
            role = await ctx.guild.create_role(name=name, colour=color)
        else:
            role = await ctx.guild.create_role(name=name)
        res = await self.create_role(name, color, ctx.guild.id, role.id)
        if res:
            await ctx.send(f"{name} created")
        else:
            await ctx.send(f"{name} already exists")

    @role.group(pass_context=True, invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx):
        _, _, name = ctx.message.content.split(" ")
        role = await self.get_role(name, ctx.guild.id)
        if role:
            g_role = ctx.guild.get_role(role.id)
            await self.remove_role(name, ctx.guild.id)
            await g_role.delete()
            await ctx.send(f"{role.name} removed")
        else:
            await ctx.send(f"{name} does not exist")

    @role.group(pass_context=True, invoke_without_command=True)
    async def join(self, ctx):
        _, _, name = ctx.message.content.split(" ")
        role = await self.get_role(name, ctx.guild.id)
        if role:
            g_role = ctx.guild.get_role(role.id)
            await ctx.message.author.add_roles(g_role)
            await ctx.send(f"<@{ctx.message.author.id}> added to {name} role")
        else:
            await ctx.send(f"{name} does not exist!")

    @role.group(pass_context=True, invoke_without_command=True)
    async def leave(self, ctx):
        _, _, name = ctx.message.content.split(" ")
        role = await self.get_role(name, ctx.guild.id)
        if role:
            g_role = ctx.guild.get_role(role.id)
            await ctx.message.author.remove_roles(g_role)
            await ctx.send(f"<@{ctx.message.author.id}> removed from {name} role")
        else:
            await ctx.send(f"{name} does not exist!")
