import os

import discord
import dotenv
from discord import app_commands as app
from discord.ext import commands

from schema import Report, User

dotenv.load_dotenv()

DEVELOPER_GUILD = discord.Object(id=os.getenv("DEVELOPER_GUILD_ID"))

def is_dev(ctx: discord.Interaction):
    if not ctx.guild or ctx.guild.id != DEVELOPER_GUILD.id: return False

    return ctx.guild.get_role(int(os.getenv("DEVELOPER_ROLE_ID"))) in ctx.user.roles

class Dev(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app.command(name="list-guilds", description="List Guilds the bot is in.")
    @app.check(is_dev)
    async def list_guilds(self, ctx: discord.Interaction):
        await ctx.response.defer()

        guilds = [guild for guild in self.bot.guilds]

        guildstr = ""
        for guild in guilds:
            owner = await self.bot.fetch_user(guild.owner_id)
            guildstr += f"- {guild.id}:\n  - **Name**: {guild.name}\n  - **Owner**: {owner.name} ({owner.id})\n"

        await ctx.followup.send(content=guildstr)
    
    @app.command(name="unban", description="Unban a User from creating Eggs.")
    @app.describe(user="The User")
    @app.check(is_dev)
    async def unban(self, ctx: discord.Interaction, user: discord.User):
        await ctx.response.defer()

        db_user = await User.get_or_none(id=user.id)

        if db_user is None:
            await ctx.followup.send(content="User not found.")
            return
        
        if not db_user.banned:
            await ctx.followup.send(content="User is not banned.")
            return
        
        db_user.banned = False
        await db_user.save(update_fields=["banned"])

        await ctx.followup.send(content=f"Unbanned user {db_user.id}.")
    
    @app.command(name="new-reports", description="Link to the top of the report queue.")
    @app.check(is_dev)
    async def new_reports(self, ctx: discord.Interaction):
        await ctx.response.defer()

        oldest_report = await Report.all().order_by("created_at").first()

        if oldest_report is None:
            await ctx.followup.send(content="Queue clear!")
            return

        reportch = self.bot.get_channel(int(os.getenv("REPORT_CHANNEL")))
        message = reportch.get_partial_message(oldest_report.log_message_id)

        await ctx.followup.send(content=message.jump_url)
    
    @app.command(name="reload", description="Reload a Cog.")
    @app.check(is_dev)
    async def reload_cog(self, ctx: discord.Interaction, cog: str):
        await self.bot.reload_extension(f"cogs.{cog}")

        await ctx.response.send_message(f"Reloaded `{cog}` module successfully.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot), guild=DEVELOPER_GUILD)