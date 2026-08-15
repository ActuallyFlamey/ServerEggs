import collections
import random
import typing

import discord
from discord import app_commands as app
from discord.ext import commands
from tortoise.functions import Count

import utils
import views
from schema import User


class Eggstras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app.command(name="collected", description="collected_description")
    @app.rename(check="collected_check", nsfw="collected_nsfw", secret="collected_secret")
    @app.describe(check="collected_check_description", nsfw="collected_nsfw_description", secret="collected_secret_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def collected(self, ctx: discord.Interaction, check: int | None, nsfw: bool | None, secret: bool | None):
        await ctx.response.defer()

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggstras/collected", lines)

        nsfw_allowed = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False

        user, _ = await User.get_or_create(id=ctx.user.id)

        if check is not None:
            egg = await user.collected.filter(id=check).prefetch_related("creator", "origin").first()

            if not egg:
                await ctx.followup.send(myloc["not_collected"].format(check))
                return

            if egg.nsfw and not nsfw_allowed:
                await ctx.followup.send(myloc["nsfw_id_in_sfw"].format(check))
                return

            collection = [egg]
        else:
            query = user.collected.all().prefetch_related("creator", "origin")

            if not nsfw_allowed:
                if nsfw:
                    await ctx.followup.send(myloc["nsfw_in_sfw"])
                    return

                query = query.filter(nsfw=False)

            if nsfw:
                query = query.filter(nsfw=True)

            if secret:
                query = query.filter(secret=True)

            collection = await query

            if not collection:
                await ctx.followup.send(myloc["empty"])
                return
        
        collection = collections.deque(collection)
        collection.rotate(random.randint(0, len(collection)))

        e, file = await utils.get_egg_embed(self.bot, lines, collection[0])

        await ctx.followup.send(
            embed=e,
            file=file or discord.utils.MISSING,
            view=views.EggLoop(self.bot, lines, myloc, ctx.user, collection) if not check else discord.utils.MISSING
        )

    leaderboard = app.Group(
        name="leaderboard",
        description="leaderboard_description",
        allowed_contexts=app.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
    )

    async def make_leaderboard(self, ctx: discord.Interaction, lbtype: typing.Literal["collections", "creations"]):
        await ctx.response.defer()

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggstras/leaderboard", lines)

        match lbtype:
            case "collections":
                field = "collected"
            case "creations":
                field = "eggs"

        collectors = await User.annotate(egg_count=Count(field)).order_by("-egg_count").limit(15).values("id", "egg_count")

        author = await User.annotate(egg_count=Count(field)).filter(id=ctx.user.id).values("egg_count")
        author_count = author[0]["egg_count"] if author else 0

        higher_count = await User.annotate(egg_count=Count(field)).filter(egg_count__gt=author_count).count()
        author_rank = higher_count + 1

        entries = []
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for idx, row in enumerate(collectors, start=1):
            uid = row["id"]
            count = row["egg_count"]

            user = self.bot.get_user(uid)
            if user is None:
                try:
                    user = await self.bot.fetch_user(uid)
                except (discord.NotFound, discord.HTTPException):
                    user = None

            name = f"**{user.display_name}** ({user.name})" if user else f"User `{uid}`"
            prefix = medals.get(idx, f"`{idx}`")

            mod = "*" if uid == ctx.user.id else ""
            who = myloc["you"] if uid == ctx.user.id else ""

            entries.append(f"{mod}{prefix} — {name}{who} — {f"{count:_}".replace("_", " ")}{mod}")
        
        if not any(row["id"] == ctx.user.id for row in collectors):
            entries.append(f"*`{author_rank}` — **{ctx.user.display_name}** ({ctx.user.name}) — {f"{author_count:_}".replace("_", " ")}*")
        
        e = discord.Embed(
            title=myloc[lbtype],
            color=discord.Color.blurple(),
            description="\n".join(entries)
        )
        utils.brand_embed(e, lines)

        await ctx.followup.send(embed=e)
    
    @leaderboard.command(name="leaderboard_collections", description="leaderboard_collections_description")
    async def lb_collections(self, ctx: discord.Interaction):
        await self.make_leaderboard(ctx, "collections")
    
    @leaderboard.command(name="leaderboard_creations", description="leaderboard_creations_description")
    async def lb_creations(self, ctx: discord.Interaction):
        await self.make_leaderboard(ctx, "creations")

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggstras(bot))