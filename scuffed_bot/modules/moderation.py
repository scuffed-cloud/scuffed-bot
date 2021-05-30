import discord.ext.commands as commands
import discord
from sqlalchemy.future import select
from sqlalchemy import delete, join
from scuffed_bot.database import Incident


class Moderation(commands.Cog):
    def __init__(self, bot, db, logger):
        self.bot = bot
        self.db = db
        self.logger = logger

    async def create_incident(self, user_id, reason, type, guild_id):
        async with self.db() as session:
            async with session.begin():
                session.add(
                    Incident(
                        user_id=user_id, reason=reason, type=type, server_id=guild_id
                    )
                )

    async def get_incidents(self, user_id, guild_id):
        async with self.db() as session:
            res = await session.execute(
                select(Incident)
                .where(Incident.user_id == user_id and Incident.server_id == guild_id)
                .order_by(Incident.create_date.desc())
            )
            return res.scalars().all()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def ban(self, ctx):
        msg_args = await util.parse_args(ctx.message.content, [])
        if 'reason' not in msg_args.keys():
            reason = None
        user = ctx.message.mentions[0]
        await ctx.guild.ban(user, reason=reason)
        await self.create_incident(user.id, reason, "ban", ctx.guild.id)
        await ctx.send(f"Banned {user.name}:{user.id}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx):
        msg_args = await util.parse_args(ctx.message.content, ['user_id'])
        for ban in await ctx.guild.bans():
            if ban.user.id == int(msg_args['user_id']):
                await ctx.guild.unban(ban.user)
                await ctx.send(f"Unbanned {ban.user.name}:{ban.user.id}")
                return
        await ctx.send(f"Ban for {msg_args['user_id']} not found")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx):
        msg_args = await util.parse_args(ctx.message.content, [])
        if 'reason' not in msg_args.keys():
            reason = None
        user = ctx.message.mentions[0]
        await ctx.guild.kick(user)
        await self.create_incident(user.id, reason, "kick", ctx.guild.id)
        await ctx.send(f"Kicked {user.name}:{user.id}")

    @commands.command()
    async def record(self, ctx):
        user = ctx.message.mentions[0]
        incidents = await self.get_incidents(user.id, ctx.guild.id)
        sheet = f"<@{user.id}> has {len(incidents)} in the record\n"
        for item in incidents:
            sheet += f"{item.create_date} reason: {item.reason} type: {item.type}\n"
        await ctx.send(sheet)
