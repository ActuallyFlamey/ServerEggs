import discord
from discord.ext import commands


async def brand_embed(e: discord.Embed, bot: commands.Bot, ctx: discord.Interaction | None = None):
    lines = await bot.get_line("embed", ctx) if ctx is not None else {
        "author": "Server Eggs",
        "footer": "Server Eggs by Flamey"
    }

    icon = "https://github.com/ActuallyFlamey/ServerEggs/blob/main/icon.png?raw=true"

    e.set_author(name=lines["author"], icon_url=icon)
    e.set_footer(text=lines["footer"], icon_url=icon)