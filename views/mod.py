import discord
from discord.ext import commands

import utils
from schema import Egg, Report

from .base import AttachmentView, RatingModal


class ReportActions(AttachmentView):
    def __init__(self, bot: commands.Bot, report, reporter, file=None, link=None, lines=None):
        super().__init__(bot, file, link, timeout=None)

        self.bot = bot
        self.report = report
        self.reporter = reporter
        self.lines = lines

        self.setup_extra("Show Extra Attachment", hide_if_missing=True)

    async def delete_reports(self, ctx: discord.Interaction, action: str, egg: Egg | int):
        all_reports = await egg.reports.all() if isinstance(egg, Egg) else await Report.filter(egg__id=egg).all()

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
        if not await utils.is_global_mod(self.bot, ctx.user.id):
            await ctx.response.send_message("Not allowed.", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="Ignore", style=discord.ButtonStyle.secondary, row=1)
    async def ignore(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg

        await self.delete_reports(ctx, "Ignore", egg.id)

    @discord.ui.button(label="Change Rating", style=discord.ButtonStyle.primary, row=1)
    async def change_rating(self, ctx: discord.Interaction, button: discord.ui.Button):
        egg = await self.report.egg

        await ctx.response.send_modal(RatingModal(self.bot.get_lines("rating", self.lines), egg, after_set=self._after_rating))

    async def _after_rating(self, ctx: discord.Interaction, egg: Egg, rating):
        await self.delete_reports(ctx, f"Change Rating to {rating.value}", egg.id)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, row=1)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg

        await self.delete_reports(ctx, "Delete", egg.id)
        await utils.egg_delete(egg)

    @discord.ui.button(label="Delete and Ban", style=discord.ButtonStyle.danger, row=1)
    async def delete_ban(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg
        creator = await egg.creator

        action = f"Delete and Ban User `{creator.id}`"

        creator.banned = True
        await creator.save(update_fields=["banned"])

        await self.delete_reports(ctx, action, egg.id)
        await utils.egg_delete(egg)