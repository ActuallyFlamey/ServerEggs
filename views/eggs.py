import collections
import os

import discord
import dotenv
from discord.ext import commands
from tortoise.exceptions import IntegrityError

import utils
from schema import Report, User

from .mod import ReportActions

dotenv.load_dotenv()

class CreateEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, myloc: dict, file: discord.Attachment | None, link: str | None):
        super().__init__(timeout=None)

        self.bot = bot
        self.myloc = myloc
        self.extrafile = file
        self.extralink = link

        self.show_extra_attachment.label = self.myloc["show_extra_attachment"]

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message(
            self.extralink,
            file=self.extrafile or discord.utils.MISSING,
            ephemeral=True
        )

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

        self.nsfw = discord.ui.Label(
            text=self.myloc["nsfw"],
            description=self.myloc["nsfw_desc"],
            component=discord.ui.Checkbox()
        )

        self.add_item(self.eggtext)
        self.add_item(self.nsfw)

    async def on_submit(self, ctx: discord.Interaction):
        await ctx.response.edit_message(content=self.myloc["success"], view=None)

        cog = self.bot.get_cog("Eggs")
        await cog.create_or_edit(ctx, None, self.eggtext.value, self.file, self.link, self.nsfw.component.value, self.secret.component.value)

class GetEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg, creator: discord.User, file: discord.Attachment | None, link: str | None):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/get", lines)
        self.egg = egg

        self.extrafile = file
        self.extralink = link

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

        self.show_extra_attachment.label = self.myloc["button"]["show_extra_attachment"]
        self.report.label = self.myloc["button"]["report"]

        if not (file or link):
            self.remove_item(self.show_extra_attachment)

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message(
            self.extralink,
            file=self.extrafile or discord.utils.MISSING,
            ephemeral=True
        )

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))

class EggLoop(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, myloc: dict, user: discord.User, eggs: collections.deque, init_extrafile: str | None, init_extralink: str | None):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = myloc
        self.user = user
        self.eggs = eggs

        self.extrafile = init_extrafile
        self.extralink = init_extralink
        self.extramsg = None

        if len(self.eggs) <= 1:
            self.prev.disabled = True
            self.next.disabled = True

        if not self.extralink:
            self.show_extra_attachment.disabled = True

        self.show_extra_attachment.label = self.myloc["show_extra_attachment"]

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

        if not inline:
            self.extrafile = file
            self.extralink = link
            self.show_extra_attachment.disabled = False

        await ctx.response.edit_message(embed=e, attachments=attachments, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.eggs.rotate(1)
        await self.respond(ctx)

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message(
            self.extralink,
            file=self.extrafile or discord.utils.MISSING,
            ephemeral=True
        )

        self.extramsg = await ctx.original_response()

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.eggs.rotate(-1)
        await self.respond(ctx)

class DeleteEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file: discord.File | None, link: str | None):
        super().__init__(timeout=60)

        self.myloc = bot.get_lines("eggs/delete", lines)
        self.egg = egg

        self.extrafile = file
        self.extralink = link

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]

        self.show_extra_attachment.label = self.myloc["show_extra_attachment"]

        if not (file or link):
            self.show_extra_attachment.disabled = True

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        eggid = self.egg.id

        await utils.egg_delete(self.egg)

        await ctx.response.edit_message(content=self.myloc["success"].format(eggid), embed=None, attachments=[], view=None)

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message(
            self.extralink,
            file=self.extrafile or discord.utils.MISSING,
            ephemeral=True
        )

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content=self.myloc["cancelled"], embed=None, attachments=[], view=None)

class PreReportEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg, file: discord.File | None, link: str | None):
        super().__init__(timeout=60)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/report", lines)
        self.egg = egg

        self.extrafile = file
        self.extralink = link

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]

        self.show_extra_attachment.label = self.myloc["show_extra_attachment"]

        if not (file or link):
            self.show_extra_attachment.disabled = True

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg))

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def show_extra_attachment(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message(
            self.extralink,
            file=self.extrafile or discord.utils.MISSING,
            ephemeral=True
        )

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

            e, file, link, inline = await utils.get_egg_embed(self.bot, self.lines, self.egg, None, True)

            msg = await reportch.send(
                content=f"New report from **{ctx.user.name}** ({reporter.id}).\n**Reason**: {report.reason}",
                embed=e,
                file=(file or discord.utils.MISSING) if inline else discord.utils.MISSING,
                view=ReportActions(self.bot, report, reporter)
            )

            related = None
            if not inline:
                related = await msg.reply(link, file=file or discord.utils.MISSING)

            report.log_message_id = msg.id
            report.related_message_id = related.id if related else None
            await report.save(update_fields=["log_message_id", "related_message_id"])

            if not self.from_report_command:
                await ctx.followup.send(content=self.myloc["success"].format(self.egg.id), ephemeral=True)
            else:
                await ctx.edit_original_response(content=self.myloc["success"].format(self.egg.id), embed=None, attachments=[], view=None)
        except IntegrityError:
            if not self.from_report_command:
                await ctx.followup.send(content=self.myloc["already"], ephemeral=True)
            else:
                await ctx.edit_original_response(content=self.myloc["already"], embed=None, attachments=[], view=None)