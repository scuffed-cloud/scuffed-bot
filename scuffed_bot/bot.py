from discord import Bot
import scuffed_bot.database as database
from scuffed_bot.modules.base import Base
from scuffed_bot.modules.tags import Tags
import logging
import importlib
import asyncio
import json

COGS = ["Base", "Tags"]


def configure_logging(file, level):
    logger = logging.getLogger("discord")
    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.handlers.WatchedFileHandler(filename=file)
    logger.addHandler(handler)


def load_config(path):
    with open(path, "r") as conf_file:
        config = json.load(conf_file)
    return config


async def load_bot(args):
    bot = Bot()
    config = load_config(args.config)
    configure_logging(config["log_file", "log_level"])
    db = await database.load_database(config["db_string"])
    bot.command_prefix = "$"
    await bot.login(config["token"])
    for cog in COGS:
        bot.add_cog(cog(bot, db, logging))
    await bot.connect()
