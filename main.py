import asyncio
import datetime
import json
import os
import re
import traceback

import discord
import dotenv
from cachetools import TTLCache
from discord import app_commands as app
from discord.ext import commands
from tortoise import Tortoise

import utils
import views
from schema import Guild, User
from tortoise_config import TORTOISE_ORM

dotenv.load_dotenv()

DEVELOPER_GUILD = discord.Object(id=int(os.getenv("DEVELOPER_GUILD_ID")))

def _resolve_lang_ref(value, root, seen):
    if not isinstance(value, str) or not value.startswith("$"):
        return value

    if value in seen:
        raise ValueError(f"Circular language reference: {value}")

    seen.add(value)

    node = root
    for part in value[1:].split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Unresolved language reference: {value}")
        node = node[part]

    return _resolve_lang_ref(node, root, seen)

def _resolve_lang_refs(obj, root):
    if isinstance(obj, dict):
        return {key: _resolve_lang_refs(val, root) for key, val in obj.items()}
    if isinstance(obj, list):
        return [_resolve_lang_refs(val, root) for val in obj]

    return _resolve_lang_ref(obj, root, set())

def load_lines_sync(file):
    with open(f"./lang/{file}", "r", encoding="utf-8") as lines:
        data = json.load(lines)

    data["lines"] = _resolve_lang_refs(data["lines"], data["lines"])

    return data

class ServerEggs(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__("", intents=discord.Intents.default())

        self.locales = {}
        self.lang_cache = TTLCache(10000, ttl=3600)

    async def setup_hook(self):
        await Tortoise.init(config=TORTOISE_ORM)

        for file in os.listdir("./lang"):
            if file.endswith(".json"):
                self.locales[file[:-5]] = await asyncio.to_thread(load_lines_sync, file)

        await self.tree.set_translator(utils.UITranslator(self))

        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"cogs.{file[:-3]}")

        await self.tree.sync()
        await self.tree.sync(guild=DEVELOPER_GUILD)

    async def get_lang(self, ctx: discord.Interaction) -> str:
        if not ctx.guild:
            cache_key = f"user_{ctx.user.id}"

            if cache_key not in self.lang_cache:
                user, _ = await User.get_or_create(id=ctx.user.id)
                self.lang_cache[cache_key] = user.lang

            return self.lang_cache[cache_key] or "en"

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

            return self.lang_cache[user_key] or self.lang_cache[guild_lang_key]
        else:
            return self.lang_cache[guild_lang_key]

    async def fetch_lines(self, ctx: discord.Interaction):
        lang = await self.get_lang(ctx)

        return self.locales.get(lang, self.locales["en"])["lines"]

    def get_lines(self, path: str, lines: dict):
        return utils.recursive_find(path, lines)

    async def get_section(self, ctx: discord.Interaction, path: str):
        lines = await self.fetch_lines(ctx)

        return lines, self.get_lines(path, lines)

    async def close(self):
        await Tortoise.close_connections()
        await super().close()

bot = ServerEggs(intents=discord.Intents.default())

@bot.event
async def on_ready():
    bot.launch_time = datetime.datetime.now(tz=datetime.timezone.utc)

    logch = bot.get_channel(int(os.getenv("DEVELOPER_LOG_CHANNEL")))
    await logch.send(f"**Server Eggs** has started on **discord.py {discord.__version__}**")

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
        value="- Set an **enticing description** for your server with `/config server-description`.\n- If you **don't want strangers** to join this server through the Eggs, use `/config privacy public:False`.\n- Set your **language** with `/config lang`, if it's **not English**.\n- If you want to **enforce your server language**, use `/config allow-user-lang allow:False`.\n- If you want to **keep track of Egg creations and edits**, use `/config log`."
    )
    e.add_field(
        name="For Server Managers",
        value="**Not always** is an **Egg worth reporting** to the global **Egg Moderators**.\nIf you feel like it's not appropriate for your members, you can simply **stop it** from **appearing here** by using `/filter`."
    )
    utils.brand_embed(e)

    systemch = guild.system_channel

    if systemch and systemch.permissions_for(guild.me).send_messages:
        await systemch.send(embed=e)
    else:
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

@bot.tree.error
async def app_command_error(ctx: discord.Interaction, error):
    lines, myloc = await bot.get_section(ctx, "error")

    e = discord.Embed(title=myloc["title"], color=0xd62450, description=str(error))
    utils.brand_embed(e, lines)

    if ctx.response.is_done():
        await ctx.followup.send(embed=e)
    else:
        await ctx.response.send_message(embed=e)

    traceback.print_exception(type(error), error, error.__traceback__)

@bot.tree.command(name="help", description="help_description")
@app.rename(about="help_about")
@app.describe(about="help_about_description")
@app.choices(about=[
    app.Choice(name=app.locale_str("create"), value="create"),
    app.Choice(name=app.locale_str("lay"), value="create"),
    app.Choice(name=app.locale_str("get"), value="get"),
    app.Choice(name=app.locale_str("egg"), value="get"),
    app.Choice(name=app.locale_str("edit"), value="edit"),
    app.Choice(name=app.locale_str("report"), value="report"),
    app.Choice(name=app.locale_str("delete"), value="delete"),
    app.Choice(name=app.locale_str("Eggify"), value="eggify"),
    app.Choice(name=app.locale_str("collected"), value="collected"),
    app.Choice(name=app.locale_str("leaderboard"), value="leaderboard"),
    app.Choice(name=app.locale_str("config"), value="config"),
    app.Choice(name=app.locale_str("filter"), value="filter")
])
@app.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help(ctx: discord.Interaction, about: str | None):
    lines, myloc = await bot.get_section(ctx, "help")

    myloc = myloc["general"] if about is None else myloc[about]

    e = discord.Embed(title=myloc["title"], color=discord.Color.blurple(), description=myloc["desc"])

    if about is None:
        e.add_field(name=myloc["about"], value=myloc["about_desc"], inline=False)
        e.add_field(name=myloc["how"], value=myloc["how_desc"], inline=False)
        e.add_field(name=myloc["donate"], value=myloc["donate_desc"], inline=False)

    utils.brand_embed(e, lines)

    await ctx.response.send_message(embed=e)

@bot.tree.context_menu(name="eggify")
@app.allowed_contexts(guilds=True, dms=False, private_channels=False)
async def eggify(ctx: discord.Interaction, message: discord.Message):
    await ctx.response.defer(ephemeral=True)

    lines, myloc = await bot.get_section(ctx, "eggs/eggify")

    file = message.attachments[0] if message.attachments else None

    content = message.content
    link = None

    url_match = re.search(r'(?<!\]\()<?(https?://[^\s>]+)>?\s*$', content)

    if url_match and not file:
        link = url_match.group(1)
        content = content[:url_match.start()].strip()

    content = utils.truncate(content, 4000)

    await ctx.followup.send(content=myloc["ready"], view=views.PreEggify(bot, lines, content, file, link), ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))