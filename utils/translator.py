import discord
from discord import app_commands as app


class UITranslator(app.Translator):
    def __init__(self, bot):
        self.bot = bot
    
    async def translate(self, line: app.locale_str, locale: discord.Locale, ctx: app.TranslationContext) -> str | None:
        lines = self.bot.locales.get(locale.value)

        if not lines and "-" in locale.value:
            lines = self.bot.locales.get(locale.value.split("-")[0])
        
        if not lines: lines = self.bot.locales.get("en")

        return lines.get(line.message)