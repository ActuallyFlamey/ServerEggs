import discord
from discord.ext import commands

import utils

from .base import AttachmentView
from .eggs import ReportEgg


class ModLogActions(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file=None, link=None):
        super().__init__(bot, file, link, timeout=None)

        self.lines = lines
        self.myloc = bot.get_lines("log", lines)
        self.egg = egg

        self.mark_nsfw.label = self.myloc["mark_nsfw"]
        self.delete.label = self.myloc["delete"]
        self.report.label = self.myloc["report"]
        self.setup_extra(self.myloc["show_extra_attachment"], hide_if_missing=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, row=1)
    async def mark_nsfw(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer(ephemeral=True)

        if not self.egg.nsfw:
            self.egg.nsfw = True
            await self.egg.save(update_fields=["nsfw"])

        await ctx.followup.send(self.myloc["marked_nsfw"].format(self.egg.id), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger, row=1)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer(ephemeral=True)

        eggid = await utils.egg_delete(self.egg)

        await ctx.followup.send(self.myloc["deleted"].format(eggid), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger, row=1)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))