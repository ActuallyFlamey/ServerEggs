import asyncio
import datetime
import json
import os

import discord
import dotenv
from cachetools import TTLCache
from discord.ext import commands
from tortoise import Tortoise

import utils
from schema import Guild, User
from tortoise_config import TORTOISE_ORM

dotenv.load_dotenv()

TESTING_GUILD = discord.Object(id=838718002412912661)

class ServerEggs(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__("", intents=discord.Intents.default())

        self.locales = {}

        self.lang_cache = TTLCache(10000, ttl=3600)
    
    async def setup_hook(self):
        await Tortoise.init(config=TORTOISE_ORM)

        def load_lines_sync(file):
            with open(f"./lang/{file}", "r", encoding="utf-8") as lines:
                return json.load(lines)
        
        for file in os.listdir("./lang"):
            if file.endswith(".json"):
                self.locales[file[:-5]] = await asyncio.to_thread(load_lines_sync, file)
        
        await self.tree.set_translator(utils.UITranslator(self))

        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"cogs.{file[:-3]}")

        self.tree.copy_global_to(guild=TESTING_GUILD)
        await self.tree.sync()
        await self.tree.sync(guild=TESTING_GUILD)

    async def get_lang(self, ctx: discord.Interaction) -> str:
        if not ctx.guild:
            cache_key = f"user_{ctx.user.id}"
            
            if cache_key not in self.lang_cache:
                user, _ = await User.get_or_create(id=ctx.user.id)
                self.lang_cache[cache_key] = user.lang
                
            return self.lang_cache[cache_key]

        guild_lang_key = f"guild_{ctx.guild.id}"
        guild_allow_key = f"guild_{ctx.guild.id}_allowuserlang"

        if guild_lang_key not in self.lang_cache or guild_allow_key not in self.lang_cache:
            guild, _ = await Guild.get_or_create(id=ctx.guild.id)
            self.lang_cache[guild_lang_key] = guild.lang
            self.lang_cache[guild_allow_key] = guild.allow_user_lang

        if self.lang_cache[guild_allow_key]:
            user_key = f"user_{ctx.user.id}"
            
            if user_key not in self.lang_cache:
                user, _ = await User.get_or_create(id=ctx.user.id)
                self.lang_cache[user_key] = user.lang
                
            return self.lang_cache[user_key]
        else:
            return self.lang_cache[guild_lang_key]
    
    async def get_line(self, path: str, ctx: discord.Interaction):
        lang = await self.get_lang(ctx)

        return utils.recursive_find("lines/" + path, self.locales.get(lang, self.locales["en"]))
    
    async def close(self):
        await Tortoise.close_connections()
        await super().close()

bot = ServerEggs(intents=discord.Intents.default())

@bot.event
async def on_ready():
    bot.launch_time = datetime.datetime.now(tz=datetime.timezone.utc)

    TESTING_CHANNEL = bot.get_channel(858733195768234035)
    await TESTING_CHANNEL.send(f"**Server Eggs** is **REBORN** on **discord.py {discord.__version__}**")

@bot.event
async def on_guild_join(guild: discord.Guild):
    invite = await guild.rules_channel.create_invite() if guild.rules_channel else await guild.text_channels[0].create_invite()

    await Guild.update_or_create(defaults={ "invite": invite.url }, id=guild.id)

    e = discord.Embed(
        title="Server Eggs",
        color=discord.Color.blurple(),
        description=f"**Server Eggs** has joined **{guild.name}**!"
    )
    e.add_field(
        name="What to do now",
        value="""
            - Set your **language** with `/config lang`, if it's **not English**.\n
            - Set an **inviting description** for your server with `/config server-description`.
        """
    )
    await utils.brand_embed(e, bot)
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                await channel.send(embed=e)
                break
            except (discord.Forbidden, discord.HTTPException):
                continue

@bot.event
async def on_guild_remove(guild: discord.Guild):
    record = await Guild.get_or_none(id=guild.id)

    if record is not None: await record.delete()

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))