import discord
from discord.ext import commands

import utils


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

async def get_egg_embed(bot: commands.Bot, lines: dict, egg, creator: discord.User = None, include_id = False):
    myloc = bot.get_line("eggs/get", lines)

    if creator is None:
        creator = bot.get_user(egg.creator.id)

        if creator is None:
            try:
                creator = await bot.fetch_user(egg.creator.id)
            except discord.NotFound:
                creator = None

    origin = bot.get_guild(egg.origin.id)

    e = discord.Embed(
        title=myloc["eggn"].format(egg.id) + (" 🌶️" if egg.nsfw else ""),
        color=discord.Color.blurple() if not egg.nsfw else discord.Color.red(),
        description=egg.text
    )
    e.add_field(
        name=myloc["creator"],
        value=f"**{creator.display_name}** ({creator.name}{f", {creator.id}" if include_id else ""})" if creator is not None else myloc["unknown_creator"].format(egg.creator.id),
        inline=False
    )
    e.add_field(
        name=myloc["origin"],
        value=f"""
            **{myloc["origin_name"]}**: {origin.name}
            {f"**{myloc["origin_desc"]}**: {egg.origin.description}" if egg.origin.description is not None else ""}
        """ if origin is not None else myloc["unknown_origin"].format(egg.origin.id),
        inline=False
    )
    utils.brand_embed(e, lines)

    file = await utils.show_attachment(egg, e)

    return e, file