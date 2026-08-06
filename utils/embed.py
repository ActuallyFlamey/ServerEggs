import discord


async def brand_embed(e: discord.Embed, lines: dict | None = None):
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