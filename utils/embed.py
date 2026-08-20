import discord
from discord.ext import commands

from schema import Rating

from . import attach, misc


def egg_title(egg, base: str) -> str:
    if egg.rating == Rating.EXPLICIT:
        marker = "🌶️"
    elif egg.rating == Rating.QUESTIONABLE:
        marker = "⚠️"
    else:
        marker = ""

    return base + (" ⭐" if egg.secret else " ") + marker

def brand_embed(e: discord.Embed, lines: dict | None = None):
    if lines is None:
        lines = {
            "embed": {
                "author": "Server Eggs",
                "footer": "Server Eggs by Flamey"
            }
        }

    icon = "https://github.com/ActuallyFlamey/ServerEggs/blob/main/icon.png?raw=true"

    e.set_author(name=lines["embed"]["author"], icon_url=icon)
    e.set_footer(text=lines["embed"]["footer"], icon_url=icon)

def get_egg_color(egg):
    color = discord.Color.blurple()

    if egg.secret and egg.rating == Rating.EXPLICIT:
        color = discord.Color.fuchsia()
    elif egg.secret:
        color = discord.Color.gold()
    elif egg.rating == Rating.EXPLICIT:
        color = discord.Color.red()
    elif egg.rating == Rating.QUESTIONABLE:
        color = discord.Color.orange()

    return color

async def get_egg_embed(bot: commands.Bot, lines: dict, egg, creator: discord.User = None, collections = None, collected = False, include_id = False):
    myloc = bot.get_lines("eggs/get", lines)

    if creator is None:
        creator = await misc.get_or_fetch_user(bot, egg.creator.id)

    origin = bot.get_guild(egg.origin.id)

    color = get_egg_color(egg)

    e = discord.Embed(
        title=egg_title(egg, myloc["eggn"].format(egg.id)),
        color=color,
        description=egg.text
    )
    e.add_field(
        name=myloc["creator"],
        value=f"**{creator.display_name}**\n({creator.name}{f", {creator.id}" if include_id else ""})" if creator is not None else myloc["unknown_creator"].format(egg.creator.id)
    )
    e.add_field(
        name=myloc["origin"],
        value=f"""
            **{myloc["origin_name"]}**: {origin.name}
            {f"**{myloc["origin_desc"]}**: {egg.origin.description}" if egg.origin.description is not None else ""}
        """ if origin is not None else myloc["unknown_origin"].format(egg.origin.id)
    )
    if collections is not None:
        e.add_field(
            name=myloc["collection_status"],
           value=myloc["collected"].format(egg.id, collections) if collected else myloc["collections"].format(egg.id, collections),
            inline=False
        )

    brand_embed(e, lines)

    file, link, inline = attach.show_attachment(egg, e)

    return e, file, link, inline