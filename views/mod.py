import os

import discord
import dotenv
from discord.ext import commands

import utils
from schema import Egg, Report

dotenv.load_dotenv()

DEVELOPER_GUILD = discord.Object(id=os.getenv("DEVELOPER_GUILD_ID"))

class ReportActions(discord.ui.View):
    def __init__(self, bot: commands.Bot, report, reporter):
        super().__init__(timeout=None)

        self.bot = bot
        self.report = report
        self.reporter = reporter

    async def delete_reports(self, ctx: discord.Interaction, action: str, egg: Egg | int):
        all_reports = await egg.reports.all() if type(egg) == Egg else await Report.filter(egg__id=egg).all()

        for report in all_reports:
            try:
                msg = ctx.channel.get_partial_message(report.log_message_id)
                await msg.edit(
                    content=self.resolved(action, egg),
                    embed=None,
                    attachments=[],
                    view=None
                )
            except discord.HTTPException:
                pass 

            await report.delete()

    def resolved(self, action: str, egg_id):
        return f"**Resolved** report `{self.report.id}`.\n**Reporter**: `{self.reporter.id}`\n**Egg**: `{egg_id}`\n**Reason**: {self.report.reason}\n**Action**: {action}"

    async def interaction_check(self, ctx: discord.Interaction):
        if ctx.guild.id != DEVELOPER_GUILD.id:
            await ctx.response.send_message("Not allowed.", ephemeral=True)
            return False

        modrole = ctx.guild.get_role(int(os.getenv("MOD_ROLE_ID")))

        if modrole not in ctx.user.roles:
            await ctx.response.send_message("Not allowed.", ephemeral=True)
            return False
        
        return True
    
    @discord.ui.button(label="Ignore", style=discord.ButtonStyle.secondary)
    async def ignore(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        action = "Ignore"

        egg = await self.report.egg

        await self.delete_reports(ctx, action, egg.id)
    
    @discord.ui.button(label="Mark NSFW", style=discord.ButtonStyle.primary)
    async def mark_nsfw(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        action = "Mark NSFW"

        egg = await self.report.egg

        if not egg.nsfw:
            egg.nsfw = True
            await egg.save(update_fields=["nsfw"])
        
        await self.delete_reports(ctx, action, egg.id)
    
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        action = "Delete"

        egg = await self.report.egg
        eggid = await utils.egg_delete(egg)

        await self.delete_reports(ctx, action, eggid)
    
    @discord.ui.button(label="Delete and Ban", style=discord.ButtonStyle.danger)
    async def delete_ban(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg
        creator = await egg.creator
        eggid = await utils.egg_delete(egg)

        action = f"Delete and Ban User `{creator.id}`"

        creator.banned = True
        await creator.save(update_fields=["banned"])

        await self.delete_reports(ctx, action, eggid)