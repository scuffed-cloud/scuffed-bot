from discord.ext.commands import Bot
import scuffed_bot.database as database
from scuffed_bot.modules.base import Base
from scuffed_bot.modules.tags import Tags
from scuffed_bot.modules.roles import Roles
from scuffed_bot.modules.moderation import Moderation
import logging
import logging.handlers
import importlib
import asyncio
import json

COGS = [Base, Tags, Roles, Moderation]


def configure_logging(file, level):
    logger = logging.getLogger("discord")
    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.handlers.WatchedFileHandler(filename=file)
    logger.addHandler(handler)
    return logger


def load_config(path):
    with open(path, "r") as conf_file:
        config = json.load(conf_file)
    return config


async def load_bot(args):
    bot = Bot(command_prefix="$")
    config = load_config(args.config)
    logger = configure_logging(config["log_file"], config["log_level"])
    db = await database.load_database(config["db_string"])
    await bot.login(config["token"])
    for cog in COGS:
        bot.add_cog(cog(bot, db, logger))
    await bot.connect()
