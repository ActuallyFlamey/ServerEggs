import os

import discord
import dotenv
from discord import app_commands as app
from discord.ext import commands

dotenv.load_dotenv()

DEVELOPER_GUILD = discord.Object(id=os.getenv("DEVELOPER_GUILD_ID"))
DEV_IDS = [int(dev_id) for dev_id in os.getenv("DEV_IDS").split(", ")]

def is_dev(ctx: discord.Interaction):
    return ctx.user.id in DEV_IDS

class Dev(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app.command(name="list-guilds", description="List Guilds the bot is in.")
    @app.describe(limit="Query limit.")
    @app.check(is_dev)
    async def list_guilds(self, ctx: discord.Interaction, limit: int = 200):
        await ctx.response.defer()

        guilds = [guild async for guild in self.bot.fetch_guilds(limit=limit)]

        guildstr = ""
        for guild in guilds:
            guildstr += f"{guild.id} - {guild.name}\n"

        await ctx.followup.send(content=guildstr)

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot), guild=DEVELOPER_GUILD)