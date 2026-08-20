import discord
from discord.ext import commands

import utils

from .base import AttachmentView, RatingModal
from .eggs import ReportEgg


class ModLogActions(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file=None, link=None):
        super().__init__(bot, file, link, timeout=None)

        self.lines = lines
        self.myloc = bot.get_lines("log", lines)
        self.egg = egg

        self.change_rating.label = self.myloc["change_rating"]
        self.delete.label = self.myloc["delete"]
        self.report.label = self.myloc["report"]
        self.setup_extra(self.myloc["show_extra_attachment"], hide_if_missing=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, row=1)
    async def change_rating(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(RatingModal(self.bot.get_lines("rating", self.lines), self.egg))

    @discord.ui.button(style=discord.ButtonStyle.danger, row=1)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer(ephemeral=True)

        eggid = await utils.egg_delete(self.egg)

        await ctx.followup.send(self.myloc["deleted"].format(eggid), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger, row=1)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))