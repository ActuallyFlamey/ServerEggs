import discord
from discord.ext import commands

import utils

from .eggs import ReportEgg


class ModLogActions(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("log", lines)
        self.egg = egg

        self.mark_nsfw.label = self.myloc["mark_nsfw"]
        self.delete.label = self.myloc["delete"]
        self.report.label = self.myloc["report"]

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def mark_nsfw(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer(ephemeral=True)

        if not self.egg.nsfw:
            self.egg.nsfw = True
            await self.egg.save(update_fields=["nsfw"])

        await ctx.followup.send(self.myloc["marked_nsfw"].format(self.egg.id), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer(ephemeral=True)

        eggid = await utils.egg_delete(self.egg)

        await ctx.followup.send(self.myloc["deleted"].format(eggid), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))