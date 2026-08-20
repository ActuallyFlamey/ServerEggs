import discord
from discord.ext import commands

import utils
from schema import Rating


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

class RatingModal(discord.ui.Modal):
    def __init__(self, myloc: dict, egg, *, after_set=None):
        self.myloc = myloc
        self.egg = egg
        self.after_set = after_set

        self.names = {
            Rating.SAFE: self.myloc["safe"],
            Rating.QUESTIONABLE: self.myloc["questionable"],
            Rating.EXPLICIT: self.myloc["explicit"],
        }

        super().__init__(title=self.myloc["title"])

        current = utils.coerce_rating(egg.rating).value

        self.rating = discord.ui.Label(
            text=self.myloc["rating"],
            description=self.myloc["rating_desc"],
            component=discord.ui.Select(
                placeholder=self.myloc["rating_placeholder"],
                options=[
                    discord.SelectOption(label=self.names[Rating.SAFE], value=Rating.SAFE.value, default=current == Rating.SAFE.value),
                    discord.SelectOption(label=self.names[Rating.QUESTIONABLE], value=Rating.QUESTIONABLE.value, default=current == Rating.QUESTIONABLE.value),
                    discord.SelectOption(label=self.names[Rating.EXPLICIT], value=Rating.EXPLICIT.value, default=current == Rating.EXPLICIT.value),
                ]
            )
        )

        self.add_item(self.rating)

    async def on_submit(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)

        rating = Rating(self.rating.component.values[0])

        self.egg.rating = rating
        await self.egg.save(update_fields=["rating"])

        await ctx.followup.send(self.myloc["success"].format(self.egg.id, self.names[rating]), ephemeral=True)

        if self.after_set:
            await self.after_set(ctx, self.egg, rating)