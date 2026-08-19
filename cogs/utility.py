import discord
from discord import app_commands as app
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app.command(name="ping", description="ping_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, ctx: discord.Interaction):
        _, myloc = await self.bot.get_section(ctx, "utility/ping")

        await ctx.response.send_message(f"**{myloc["latency"]}**: {round(self.bot.latency * 1000, 1)}ms")

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))