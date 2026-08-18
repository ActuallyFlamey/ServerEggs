import discord
from discord.ext import commands

import utils


class AttachmentView(discord.ui.View):
    """View with a shared "show extra attachment" button for non-inline media."""

    def __init__(self, bot: commands.Bot, file=None, link=None, *, timeout: float | None = None):
        super().__init__(timeout=timeout)

        self.bot = bot
        self.extrafile = file
        self.extralink = link

    def setup_extra(self, label: str, *, style=None, hide_if_missing: bool = False, disable_if_missing: bool = False):
        button = self.show_extra_attachment
        button.label = label

        if style is not None:
            button.style = style

        if not (self.extrafile or self.extralink):
            if hide_if_missing:
                self.remove_item(button)
            elif disable_if_missing:
                button.disabled = True

    def reorder(self, order: list[str]):
        present = {id(item) for item in self.children}

        ordered = []
        for name in order:
            item = getattr(self, name)
            if id(item) in present:
                ordered.append(item)

        for item in self.children:
            self.remove_item(item)
        for item in ordered:
            self.add_item(item)

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await utils.send_extra(ctx, self.extrafile, self.extralink)