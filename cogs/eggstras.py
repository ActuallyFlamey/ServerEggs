import collections
import random
import re
import unicodedata

import discord
from discord import app_commands as app
from discord.ext import commands
from tortoise.expressions import Q

import utils
import views
from schema import Egg, User

CUSTOM_EMOJI_RE = re.compile(r"<a?:(\w+):\d+>")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
AUTOLINK_RE = re.compile(r"<(\w+://[^>]+)>")

EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0x2B00, 0x2BFF),
)

def is_emoji(code: int) -> bool:
    return any(start <= code <= end for start, end in EMOJI_RANGES)

EMOJI_ALIASES = {}
for start, end in EMOJI_RANGES:
    for code in range(start, end + 1):
        name = unicodedata.name(chr(code), None)
        if not name:
            continue
        for _word in name.lower().split():
            EMOJI_ALIASES.setdefault(_word, set()).add(chr(code))

def normalize(text: str) -> str:
    text = CUSTOM_EMOJI_RE.sub(r"\1", text)
    text = LINK_RE.sub(r"\1 \2", text)
    text = AUTOLINK_RE.sub(r"\1", text)

    out = []
    for ch in text:
        if is_emoji(ord(ch)):
            name = unicodedata.name(ch, "")
            if name:
                out.append(name)
                continue
        out.append(ch)

    return "".join(out).lower()

def expand(text: str) -> set[str]:
    terms = {text}

    terms.update(CUSTOM_EMOJI_RE.findall(text))

    for ch in text:
        if is_emoji(ord(ch)):
            terms.add(ch)
            name = unicodedata.name(ch, "")
            if name:
                terms.add(name)
                terms.update(name.lower().split())

    for word in re.findall(r"[a-z0-9']+", text.lower()):
        terms.update(EMOJI_ALIASES.get(word, ()))

    return terms

class Eggstras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def egg_loop(self, ctx: discord.Interaction, mode: str, check: int | None, nsfw: bool | None, secret: bool | None):
        await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggstras/loop")

        nsfw_allowed = utils.channel_is_nsfw(ctx.channel)

        user, _ = await User.get_or_create(id=ctx.user.id)

        match mode:
            case "collected":
                field = user.collected
            case "created":
                field = user.eggs

        if check is not None:
            egg = await field.filter(id=check).prefetch_related("creator", "origin").first()

            if not egg:
                await ctx.followup.send(myloc[f"not_{mode}"].format(check))
                return

            if egg.nsfw and not nsfw_allowed:
                await ctx.followup.send(myloc["nsfw_id_in_sfw"].format(check))
                return

            loop = [egg]
        else:
            query = field.all().prefetch_related("creator", "origin")

            if not nsfw_allowed:
                if nsfw:
                    await ctx.followup.send(myloc["nsfw_in_sfw"])
                    return

                query = query.filter(nsfw=False)

            if nsfw:
                query = query.filter(nsfw=True)

            if secret:
                query = query.filter(secret=True)

            loop = await query

            if not loop:
                await ctx.followup.send(myloc["empty"])
                return

        eggs = collections.deque(loop)
        eggs.rotate(random.randint(0, len(eggs)))

        e, file, link, inline = await utils.get_egg_embed(self.bot, lines, eggs[0])
        sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

        await ctx.followup.send(
            embed=e,
            file=sfile,
            view=views.EggLoop(
                self.bot, lines, myloc, ctx.user, eggs,
                vfile, vlink
            ) if not check else discord.utils.MISSING
        )

    @app.command(name="collected", description="collected_description")
    @app.rename(check="collected_check", nsfw="collected_nsfw", secret="collected_secret")
    @app.describe(check="collected_check_description", nsfw="collected_nsfw_description", secret="collected_secret_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def collected(self, ctx: discord.Interaction, check: int | None, nsfw: bool | None, secret: bool | None):
        await self.egg_loop(ctx, "collected", check, nsfw, secret)

    @app.command(name="my-eggs", description="my-eggs_description")
    @app.rename(check="my-eggs_check", nsfw="my-eggs_nsfw", secret="my-eggs_secret")
    @app.describe(check="my-eggs_check_description", nsfw="my-eggs_nsfw_description", secret="my-eggs_secret_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def my_eggs(self, ctx: discord.Interaction, check: int | None, nsfw: bool | None, secret: bool | None):
        await self.egg_loop(ctx, "created", check, nsfw, secret)

    @app.command(name="search", description="search_description")
    @app.rename(text="search_text")
    @app.describe(text="search_text_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def search(self, ctx: discord.Interaction, text: str):
        await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggstras/search")

        nsfw_allowed = utils.channel_is_nsfw(ctx.channel)

        query = text.strip()

        if not query:
            await ctx.followup.send(myloc["empty"].format(text))
            return

        sql = Q(text__icontains=query)
        for alt in expand(query) - {query}:
            sql |= Q(text__icontains=alt)

        q = Egg.all().prefetch_related("creator", "origin").filter(sql)
        q = q.filter(secret=False)
        if not nsfw_allowed:
            q = q.filter(nsfw=False)

        if ctx.guild:
            filtered = await Egg.filter(filtered_in__id=ctx.guild.id).values_list("id", flat=True)
            if filtered:
                q = q.filter(id__not_in=filtered)

        eggs = await q

        norm_query = normalize(query)

        eggs = [egg for egg in eggs if norm_query in normalize(egg.text or "")]

        if not eggs:
            await ctx.followup.send(myloc["empty"].format(query))
            return

        eggs.sort(key=lambda egg: (
            normalize(egg.text or "") != norm_query,
            not normalize(egg.text or "").startswith(norm_query),
            len(egg.text or ""),
            egg.id,
        ))

        loop = collections.deque(eggs)

        e, file, link, inline = await utils.get_egg_embed(self.bot, lines, loop[0])
        sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

        await ctx.followup.send(
            embed=e,
            file=sfile,
            view=views.EggLoop(
                self.bot, lines, myloc, ctx.user, loop,
                vfile, vlink
            )
        )

    leaderboard = app.Group(
        name="leaderboard",
        description="leaderboard_description",
        allowed_contexts=app.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
    )

    async def _user_name(self, bot, user_id: int) -> str:
        user = await utils.get_or_fetch_user(bot, user_id)

        if user is None:
            return f"User `{user_id}`"

        return f"**{user.display_name}** ({discord.utils.escape_markdown(user.name, as_needed=False)})"

    async def _send_leaderboard(self, ctx: discord.Interaction, leaderboard: utils.Leaderboard, title_key: str, name_resolver, self_id: int):
        await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggstras/leaderboard")

        entries = await utils.render_entries(self.bot, leaderboard, self_id, name_resolver, myloc["you"])

        e = discord.Embed(
            title=myloc[title_key],
            color=discord.Color.blurple(),
            description="\n".join(entries)
        )
        utils.brand_embed(e, lines)

        await ctx.followup.send(embed=e)

    @leaderboard.command(name="leaderboard_collections", description="leaderboard_collections_description")
    async def lb_collections(self, ctx: discord.Interaction):
        await self._send_leaderboard(ctx, utils.Leaderboard(User, "collected"), "collections", self._user_name, ctx.user.id)

    @leaderboard.command(name="leaderboard_creations", description="leaderboard_creations_description")
    async def lb_creations(self, ctx: discord.Interaction):
        await self._send_leaderboard(ctx, utils.Leaderboard(User, "eggs"), "creations", self._user_name, ctx.user.id)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggstras(bot))