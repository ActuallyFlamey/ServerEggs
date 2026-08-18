import discord
from discord.ext import commands

import utils
import views

from .embed import get_egg_embed


async def log_egg(bot: commands.Bot, lines: dict, guild, egg, creator: discord.User, actor: discord.User, edit: bool = False):
    myloc = bot.get_lines("eggs/create_edit", lines)

    logch = bot.get_channel(guild.logch)

    if not logch: return

    e, file, link, inline = await get_egg_embed(bot, lines, egg, creator)
    sfile, _, _ = utils.attachment_kwargs(file, link, inline)

    log = await logch.send(
        myloc["log"].format(
            actor.display_name,
            actor.name,
            myloc["edited"] if edit else myloc["created"],
            egg.id
        ),
        embed=e,
        file=sfile,
        view=views.ModLogActions(bot, lines, egg)
    )
    if not inline: await log.reply(link, file=file or discord.utils.MISSING)