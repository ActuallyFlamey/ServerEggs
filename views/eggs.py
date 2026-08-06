import os

import discord
import dotenv
from discord.ext import commands

import utils

dotenv.load_dotenv()

class GetEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg, creator: discord.User):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_line("eggs/get", lines)
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
        e = discord.Embed(title=self.myloc["report"]["title"], color=discord.Color.red, description=self.myloc["report"]["confirm"])
        e.add_field(name=self.myloc["report"]["rules_title"], value=self.myloc["report"]["rules"])
        e.add_field(name=self.myloc["report"]["agree_title"], value=self.myloc["report"]["rules"])
        await utils.brand_embed(e, self.lines)

        await ctx.response.send_message(embed=e, view=ReportEgg(self.bot, self.lines, self.egg), ephemeral=True)

class DeleteEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg):
        super().__init__(timeout=60)
        
        self.myloc = bot.get_line("eggs/delete", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
    
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

class ReportEgg(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, egg):
        super().__init__(timeout=60)

        self.myloc = bot.get_line("eggs/report", lines)
        self.egg = egg

        self.confirm.label = self.myloc["confirm"]
    
    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        ...