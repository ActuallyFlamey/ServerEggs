import collections
import os

import discord
import dotenv
from discord.ext import commands
from tortoise.exceptions import IntegrityError

import utils
from schema import Rating, Report, User

from .base import AttachmentView
from .mod import ReportActions

dotenv.load_dotenv()

class CreateEgg(AttachmentView):
    def __init__(self, bot: commands.Bot, myloc: dict, file, link):
        super().__init__(bot, file, link, timeout=None)

        self.myloc = myloc

        self.setup_extra(self.myloc["show_extra_attachment"], hide_if_missing=True)

class PreEggify(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, text: str | None, file: discord.Attachment | None, link: str | None):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/eggify", lines)
        self.text = text
        self.file = file
        self.link = link

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(Eggify(self.bot, self.lines, self.text, self.file, self.link))

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content=self.myloc["cancelled"], embed=None, attachments=[], view=None)

class Eggify(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, lines: dict, text: str | None, file: discord.Attachment | None, link: str | None):
        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/eggify", lines)

        self.text = text
        self.file = file
        self.link = link

        super().__init__(title=self.myloc["title"])

        self.eggtext = discord.ui.TextInput(
            label=self.myloc["text"],
            placeholder=self.myloc["text_placeholder"],
            default=text,
            required=False,
            style=discord.TextStyle.paragraph
        )

        self.secret = discord.ui.Label(
            text=self.myloc["secret"],
            description=self.myloc["secret_desc"],
            component=discord.ui.Checkbox()
        )

        self.rating = discord.ui.Label(
            text=self.myloc["rating"],
            description=self.myloc["rating_desc"],
            component=discord.ui.Select(
                placeholder=self.myloc["rating_placeholder"],
                options=[
                    discord.SelectOption(label=self.myloc["rating_safe"], value=Rating.SAFE.value),
                    discord.SelectOption(label=self.myloc["rating_questionable"], value=Rating.QUESTIONABLE.value),
                    discord.SelectOption(label=self.myloc["rating_explicit"], value=Rating.EXPLICIT.value),
                ]
            )
        )

        self.add_item(self.eggtext)
        self.add_item(self.rating)

    async def on_submit(self, ctx: discord.Interaction):
        await ctx.response.edit_message(content=self.myloc["success"], view=None)

        cog = self.bot.get_cog("Eggs")
        await cog.create_or_edit(ctx, None, self.eggtext.value, self.file, self.link, Rating(self.rating.component.values[0]), self.secret.component.value)

class GetEgg(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, egg, creator: discord.User, file=None, link=None):
        super().__init__(bot, file, link, timeout=None)

        self.lines = lines
        self.myloc = bot.get_lines("eggs/get", lines)
        self.egg = egg

        if egg.origin.invite is not None:
            self.add_item(
                discord.ui.Button(
                    label=self.myloc["button"]["origin"],
                    url=egg.origin.invite,
                    row=1
                )
            )

        if creator is not None:
            self.add_item(
                discord.ui.Button(
                    label=self.myloc["button"]["creator"],
                    url=f"https://discord.com/users/{creator.id}",
                    row=1
                )
            )

        self.report.label = self.myloc["button"]["report"]
        self.setup_extra(self.myloc["button"]["show_extra_attachment"], hide_if_missing=True)

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))

class EggLoop(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, myloc: dict, user: discord.User, eggs: collections.deque, init_extrafile=None, init_extralink=None):
        super().__init__(bot, init_extrafile, init_extralink, timeout=None)

        self.lines = lines
        self.myloc = myloc
        self.user = user
        self.eggs = eggs
        self.extramsg = None

        if len(self.eggs) <= 1:
            self.prev.disabled = True
            self.next.disabled = True

        self.setup_extra(self.myloc["show_extra_attachment"], style=discord.ButtonStyle.secondary, disable_if_missing=True)
        self.reorder(["prev", "show_extra_attachment", "next"])

    async def interaction_check(self, ctx: discord.Interaction):
        if ctx.user.id != self.user.id:
            await ctx.response.send_message(self.myloc["not_yours"], ephemeral=True)
            return False

        return True

    async def respond(self, ctx: discord.Interaction):
        if self.extramsg:
            await self.extramsg.delete()

        e, file, link, inline = await utils.get_egg_embed(self.bot, self.lines, self.eggs[0])

        attachments = []
        if inline:
            if file:
                attachments = [file]

            self.show_extra_attachment.disabled = True
        else:
            self.extrafile = utils.file_path(file)
            self.extralink = link
            self.show_extra_attachment.disabled = False

        await ctx.response.edit_message(embed=e, attachments=attachments, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.eggs.rotate(1)
        await self.respond(ctx)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.eggs.rotate(-1)
        await self.respond(ctx)

class DeleteEgg(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file=None, link=None):
        super().__init__(bot, file, link, timeout=60)

        self.myloc = bot.get_lines("eggs/delete", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]
        self.setup_extra(self.myloc["show_extra_attachment"], style=discord.ButtonStyle.secondary, disable_if_missing=True)
        self.reorder(["confirm", "show_extra_attachment", "cancel"])

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        eggid = self.egg.id

        await utils.egg_delete(self.egg)

        await ctx.response.edit_message(content=self.myloc["success"].format(eggid), embed=None, attachments=[], view=None)

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content=self.myloc["cancelled"], embed=None, attachments=[], view=None)

class PreReportEgg(AttachmentView):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file=None, link=None):
        super().__init__(bot, file, link, timeout=60)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/report", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]
        self.setup_extra(self.myloc["show_extra_attachment"], style=discord.ButtonStyle.secondary, disable_if_missing=True)
        self.reorder(["confirm", "show_extra_attachment", "cancel"])

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg))

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content=self.myloc["cancelled"], embed=None, attachments=[], view=None)

class ReportEgg(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, lines: dict, egg, from_report_command = True):
        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/report", lines)
        self.egg = egg
        self.from_report_command = from_report_command

        super().__init__(title=self.myloc["title"].format(egg.id))

        self.reason = discord.ui.Label(
            text=self.myloc["rule"],
            description=self.myloc["rule_desc"],
            component=discord.ui.Select(
                placeholder=self.myloc["rule_placeholder"],
                options=[
                    discord.SelectOption(label=self.myloc["rules"]["unmarkednsfw"], description=self.myloc["rules"]["unmarkednsfw_desc"]),
                    discord.SelectOption(label=self.myloc["rules"]["hateful"], description=self.myloc["rules"]["hateful_desc"]),
                    discord.SelectOption(label=self.myloc["rules"]["other"], description=self.myloc["rules"]["other_desc"]),
                ]
            )
        )

        self.specify = discord.ui.TextInput(
            label=self.myloc["other"],
            required=False,
            max_length=200,
            placeholder=self.myloc["other_placeholder"]
        )

        self.add_item(self.reason)
        self.add_item(self.specify)

    async def _finish(self, ctx: discord.Interaction, key: str):
        content = self.myloc[key].format(self.egg.id)

        if self.from_report_command:
            await ctx.edit_original_response(content=content, embed=None, attachments=[], view=None)
        else:
            await ctx.followup.send(content=content, ephemeral=True)

    async def on_submit(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)

        reporter, _ = await User.get_or_create(id=ctx.user.id)

        reason = self.reason.component.values[0]
        if reason == self.myloc["rules"]["other"]:
            reason = self.specify.value

        try:
            report = await Report.create(
                egg=self.egg,
                reporter=reporter,
                reason=reason
            )

            reportch = self.bot.get_channel(int(os.getenv("REPORT_CHANNEL")))

            e, file, link, inline = await utils.get_egg_embed(self.bot, self.lines, self.egg, None, None, False, True)
            sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

            msg = await reportch.send(
                content=f"New report from **{ctx.user.name}** ({reporter.id}).\n**Reason**: {report.reason}",
                embed=e,
                file=sfile,
                view=ReportActions(
                    self.bot, report, reporter,
                    vfile, vlink, lines=self.lines
                )
            )

            report.log_message_id = msg.id
            await report.save(update_fields=["log_message_id"])

            await self._finish(ctx, "success")
        except IntegrityError:
            await self._finish(ctx, "already")