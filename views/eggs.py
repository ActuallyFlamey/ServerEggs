import os

import discord
import dotenv
from discord.ext import commands
from tortoise.exceptions import IntegrityError

import utils
from schema import Report, User

from .mod import ReportActions

dotenv.load_dotenv()

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
        await cog.create_or_edit(ctx, None, self.eggtext.value, self.file, self.link, self.nsfw.component.value)

class GetEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg, creator: discord.User):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/get", lines)
        self.egg = egg

        if egg.origin.invite is not None:
            self.add_item(
                discord.ui.Button(
                    label=self.myloc["button"]["origin"],
                    url=egg.origin.invite
                )
            )
        
        if creator is not None:
            self.add_item(
                discord.ui.Button(
                    label=self.myloc["button"]["creator"],
                    url=f"https://discord.com/users/{creator.id}"
                )
            )
        
        self.report.label = self.myloc["button"]["report"]
    
    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def report(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(ReportEgg(self.bot, self.lines, self.egg, False))

class DeleteEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg):
        super().__init__(timeout=60)
        
        self.myloc = bot.get_lines("eggs/delete", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]
    
    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        if self.egg.attach_path and os.path.exists(self.egg.attach_path):
            try:
                os.remove(self.egg.attach_path)
            except OSError:
                print(f"log: failed to delete attachment for Egg {self.egg.id}")
        
        eggid = self.egg.id

        await self.egg.delete()

        await ctx.response.edit_message(content=self.myloc["success"].format(eggid), embed=None, attachments=[], view=None)
    
    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content=self.myloc["cancelled"], embed=None, attachments=[], view=None)

class PreReportEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg):
        super().__init__(timeout=60)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("eggs/report", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
        self.cancel.label = self.myloc["cancel"]
    
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

            e, file = await utils.get_egg_embed(self.bot, self.lines, self.egg, None, True)

            msg = await reportch.send(
                content=f"New report from **{ctx.user.name}** ({reporter.id}).\n**Reason**: {report.reason}",
                embed=e,
                file=file or discord.utils.MISSING,
                view=ReportActions(self.bot, report, reporter)
            )

            report.log_message_id = msg.id
            await report.save(update_fields=["log_message_id"])

            if not self.from_report_command:
                await ctx.followup.send(content=self.myloc["success"].format(self.egg.id), ephemeral=True)
            else:
                await ctx.edit_original_response(content=self.myloc["success"].format(self.egg.id), embed=None, attachments=[], view=None)
        except IntegrityError:
            if not self.from_report_command:
                await ctx.followup.send(content=self.myloc["already"], ephemeral=True)
            else:
                await ctx.edit_original_response(content=self.myloc["already"], embed=None, attachments=[], view=None)