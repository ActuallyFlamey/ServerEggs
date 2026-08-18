import collections
import random

import discord
from discord import app_commands as app
from discord.ext import commands

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

        lines, myloc = await self.bot.get_section(ctx, "eggstras/collected")

        nsfw_allowed = utils.channel_is_nsfw(ctx.channel)

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

        e, file, link, inline = await utils.get_egg_embed(self.bot, lines, collection[0])
        sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

        await ctx.followup.send(
            embed=e,
            file=sfile,
            view=views.EggLoop(
                self.bot, lines, myloc, ctx.user, collection,
                vfile, vlink
            ) if not check else discord.utils.MISSING
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