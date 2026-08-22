import discord

import utils
from schema import Rating


class ExtraAttachmentButton(discord.ui.Button):
    """Sends the Egg's non-gallery media (audios and unfurlable page links) in its own message."""

    def __init__(self, label: str, *, style=discord.ButtonStyle.primary, file=None, link=None):
        super().__init__(label=label, style=style, custom_id="servereggs:extra_attachment")

        self.extrafile = file
        self.extralink = link

    async def callback(self, ctx: discord.Interaction):
        await utils.send_extra(ctx, self.extrafile, self.extralink)

def action_button(label: str, style, callback) -> discord.ui.Button:
    button = discord.ui.Button(label=label, style=style)
    button.callback = callback
    return button

def text_view(content: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.TextDisplay(content))

    return view

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
