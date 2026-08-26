import discord
from discord import app_commands as app
from discord.ext import commands
from tortoise.expressions import Q

import utils
import views
from schema import Egg, Guild, Rating, User


class Eggs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def manage_check(self, ctx: discord.Interaction, egg):
        creatorchk = ctx.user.id == egg.creator.id

        modchk = ctx.guild and ctx.permissions.manage_guild and egg.origin.id == ctx.guild.id

        globalmodchk = await utils.is_global_mod(self.bot, ctx.user.id)

        return creatorchk or modchk or globalmodchk

    async def create_or_edit(
        self,
        ctx: discord.Interaction,
        id: int | None = None,
        text: str | None = None,
        file: discord.Attachment | None = None,
        link: str | None = None,
        rating: Rating | None = None,
        secret: bool | None = None
    ):
        rating = utils.coerce_rating(rating)

        if not ctx.response.is_done():
            await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggs/create_edit")

        if not id:
            if text is None and file is None and link is None:
                await ctx.followup.send(myloc["empty_create"])
                return
        else:
            if text is None and file is None and link is None and secret is None and rating is None:
                await ctx.followup.send(myloc["empty_edit"])
                return

        guild = None
        if ctx.guild:
            guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if rating is not None and rating not in utils.channel_ratings(guild, ctx.channel):
            await ctx.followup.send(myloc["rating_not_allowed"])
            return

        if file and link:
            await ctx.followup.send(myloc["toomanyattach"])
            return

        user, _ = await User.get_or_create(id=ctx.user.id)
        if user.banned:
            await ctx.followup.send(myloc["banned"])
            return

        egg = None
        if id:
            egg = await Egg.get_with_related(id)

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id), ephemeral=True)
                return

            if not await self.manage_check(ctx, egg):
                await ctx.followup.send(myloc["cannot"], ephemeral=True)
                return

        trimtext = None
        if text is not None:
            text = text.strip() or None
            trimtext = utils.truncate(text, 4000)

        attach_path = attach_hash = attach_link = scanfile = attach_bytes = None
        if file:
            content_type = utils.get_content_type(file)

            if not file.content_type or content_type not in {"image", "video", "audio"}:
                await ctx.followup.send(myloc["supported_only"])
                return

            if file.size and file.size > utils.UPLOAD_LIMIT:
                await ctx.followup.send(myloc["too_big"])
                return

            scanfile = await file.to_file()
        elif link:
            attach_link = await utils.resolve_media_url(link)
            if attach_link is None:
                await ctx.followup.send(myloc["invalid_url"])
                return

            if not utils.is_native_embed(attach_link):
                scanfile = await utils.url_to_file(attach_link)
                if not scanfile:
                    await ctx.followup.send(myloc["could_not_scan"])
                    return

        processing = await ctx.followup.send(myloc["processing"])

        if scanfile:
            scan, too_long, attach_bytes = await utils.scan_csam(scanfile)

            if too_long:
                await processing.edit(content=myloc["too_big"])
                return

            if scan:
                await processing.edit(content=myloc["illegal"])

                user.banned = True
                await user.save()

                return

        if file:
            try:
                attach_path, attach_hash = await utils.process_attachment(file, attach_bytes)
            except utils.UnsupportedMedia:
                await processing.edit(content=myloc["supported_only"])
                return

            if not attach_path:
                await processing.edit(content=myloc["convert_failed"])
                return

        check_text = trimtext if text is not None else (egg.text if id else None)
        check_hash = attach_hash if file else (None if link else (egg.attach_hash if id else None))
        check_link = attach_link if link else (None if file else (egg.attach_link if id else None))

        checks = []
        if check_hash:
            checks.append(Q(attach_hash=check_hash))
        if check_link:
            checks.append(Q(attach_link=check_link))
        if not checks and check_text is not None:
            checks.append(Q(text=check_text, attach_hash=None, attach_link=None))

        existing = None
        if checks:
            combined = checks[0]
            for cond in checks[1:]:
                combined |= cond

            query = Egg.exclude(id=id) if id else Egg.all()
            existing = await query.filter(combined).first()

        if existing:
            utils.safe_remove(attach_path)

            await processing.edit(content=myloc["duplicate"].format(existing.id))
            return

        if not id:
            egg = await Egg.create(
                text=trimtext,
                attach_path=attach_path,
                attach_hash=attach_hash,
                attach_link=attach_link,
                rating=rating or Rating.SAFE,
                secret=secret or False,
                creator=user,
                origin=guild
            )
        else:
            if (file or link):
                utils.safe_remove(egg.attach_path)

            if text is not None: egg.text = trimtext
            if file is not None or link is not None:
                egg.attach_path = attach_path
                egg.attach_hash = attach_hash
                egg.attach_link = attach_link
            if rating is not None: egg.rating = rating
            if secret is not None: egg.secret = secret

            await egg.save()

        creator = self.bot.get_user(egg.creator.id)
        if ctx.guild: await utils.log_egg(self.bot, lines, guild, egg, creator, ctx.user, bool(id))

        container, resfile, vfile, vlink = await utils.get_egg_layout(
            self.bot, lines, egg,
            title=utils.egg_title(egg, myloc["title"].format(egg.id, myloc["created"] if not id else myloc["edited"])),
            created=not id
        )

        await processing.edit(
            content=None,
            attachments=[resfile] if resfile else [],
            view=views.CreateEgg(myloc, container, vfile, vlink)
        )

    @app.command(name="create", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", rating="create_rating", secret="create_secret")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", rating="create_rating_description", secret="create_secret_description")
    @app.choices(rating=[
        app.Choice(name=app.locale_str("rating_safe"), value=Rating.SAFE),
        app.Choice(name=app.locale_str("rating_questionable"), value=Rating.QUESTIONABLE),
        app.Choice(name=app.locale_str("rating_explicit"), value=Rating.EXPLICIT),
    ])
    @app.allowed_installs(guilds=True, users=False)
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def create(
        self,
        ctx: discord.Interaction,
        text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        rating: Rating | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, None, text, file, link, rating, secret)

    @app.command(name="lay", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", rating="create_rating")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", rating="create_rating_description")
    @app.choices(rating=[
        app.Choice(name=app.locale_str("rating_safe"), value=Rating.SAFE),
        app.Choice(name=app.locale_str("rating_questionable"), value=Rating.QUESTIONABLE),
        app.Choice(name=app.locale_str("rating_explicit"), value=Rating.EXPLICIT),
    ])
    @app.allowed_installs(guilds=True, users=False)
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def lay(
        self,
        ctx: discord.Interaction,
        text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        rating: Rating | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, None, text, file, link, rating, secret)

    async def _get(self, ctx: discord.Interaction, id: int | None, rating: Rating | None):
        await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggs/get")

        guild = await Guild.get_or_none(id=ctx.guild.id) if ctx.guild else None
        allowed = utils.channel_ratings(guild, ctx.channel)

        collected = False

        if id is not None:
            egg = await Egg.get_with_related(id)

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id))
                return

            if egg.rating not in allowed:
                await ctx.followup.send(myloc["id_rating_not_allowed"].format(id))
                return

            if egg.secret:
                await ctx.followup.send(myloc["secret"].format(id))
                return

            if ctx.guild and await egg.filtered_in.filter(id=ctx.guild.id).exists():
                await ctx.followup.send(myloc["filtered"].format(id, ctx.guild.name))
                return
        else:
            if rating and rating not in allowed:
                await ctx.followup.send(myloc["rating_not_allowed"])
                return

            egg = await utils.random_egg(guild, ctx.channel, rating=rating)

            if egg is None:
                await ctx.followup.send(myloc["no_egg"])
                return

            user, _ = await User.get_or_create(id=ctx.user.id)
            if not await user.collected.filter(id=egg.id).exists():
                await user.collected.add(egg)
                collected = True

        creator = await utils.get_or_fetch_user(self.bot, egg.creator.id)

        container, sfile, vfile, vlink = await utils.get_egg_layout(self.bot, lines, egg, creator, collected)

        await ctx.followup.send(
            file=sfile or discord.utils.MISSING,
            view=views.GetEgg(self.bot, lines, egg, guild, creator, container, vfile, vlink)
        )

    @app.command(name="get", description="get_description")
    @app.rename(id="get_id", rating="get_rating")
    @app.describe(id="get_id_description", rating="get_rating_description")
    @app.choices(rating=[
        app.Choice(name=app.locale_str("rating_safe"), value=Rating.SAFE),
        app.Choice(name=app.locale_str("rating_questionable"), value=Rating.QUESTIONABLE),
        app.Choice(name=app.locale_str("rating_explicit"), value=Rating.EXPLICIT),
    ])
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def get(self, ctx: discord.Interaction, id: int | None, rating: Rating | None):
        await self._get(ctx, id, rating)

    @app.command(name="egg", description="get_description")
    @app.rename(id="get_id", rating="get_rating")
    @app.describe(id="get_id_description", rating="get_rating_description")
    @app.choices(rating=[
        app.Choice(name=app.locale_str("rating_safe"), value=Rating.SAFE),
        app.Choice(name=app.locale_str("rating_questionable"), value=Rating.QUESTIONABLE),
        app.Choice(name=app.locale_str("rating_explicit"), value=Rating.EXPLICIT),
    ])
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def egg(self, ctx: discord.Interaction, id: int | None, rating: Rating | None):
        await self._get(ctx, id, rating)

    @app.command(name="nsfw", description="nsfw_description", nsfw=True)
    async def nsfw(self, ctx: discord.Interaction):
        await self._get(ctx, None, Rating.EXPLICIT)
    
    @app.command(name="latest", description="latest_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def latest(self, ctx: discord.Interaction):
        await ctx.response.defer()

        lines = await self.bot.fetch_lines(ctx)

        guild = await Guild.get_or_none(id=ctx.guild.id) if ctx.guild else None
        allowed = utils.channel_ratings(guild, ctx.channel)

        filtered = []
        if ctx.guild:
            filtered = await Egg.filter(filtered_in__id=ctx.guild.id).values_list("id", flat=True)

        egg = await Egg.filter(rating__in=allowed, id__not_in=filtered, secret=False).order_by("-created_at").prefetch_related("creator", "origin").first()

        creator = await utils.get_or_fetch_user(self.bot, egg.creator.id)

        container, sfile, vfile, vlink = await utils.get_egg_layout(self.bot, lines, egg, creator)

        await ctx.followup.send(
            file=sfile or discord.utils.MISSING,
            view=views.GetEgg(self.bot, lines, egg, guild, creator, container, vfile, vlink)
        )

    @app.command(name="edit", description="edit_description")
    @app.rename(id="edit_id", text="edit_text", file="edit_file", link="edit_link", rating="edit_rating", secret="edit_secret")
    @app.describe(id="edit_id_description", text="edit_text_description", file="edit_file_description", link="edit_link_description", rating="edit_rating_description", secret="edit_secret_description")
    @app.choices(rating=[
        app.Choice(name=app.locale_str("rating_safe"), value=Rating.SAFE),
        app.Choice(name=app.locale_str("rating_questionable"), value=Rating.QUESTIONABLE),
        app.Choice(name=app.locale_str("rating_explicit"), value=Rating.EXPLICIT),
    ])
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def edit(
        self,
        ctx: discord.Interaction,
        id: int, text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        rating: Rating | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, id, text, file, link, rating, secret)

    async def _confirm_flow(self, ctx: discord.Interaction, path: str, id: int, view_class, *, check_manage: bool = False):
        await ctx.response.defer(ephemeral=True)

        lines, myloc = await self.bot.get_section(ctx, path)

        egg = await Egg.get_with_related(id)

        if not egg:
            await ctx.followup.send(myloc["not_found"].format(id), ephemeral=True)
            return

        if check_manage and not await self.manage_check(ctx, egg):
            await ctx.followup.send(myloc["cannot"], ephemeral=True)
            return

        container, sfile, vfile, vlink = await utils.get_egg_layout(self.bot, lines, egg)

        await ctx.followup.send(
            file=sfile or discord.utils.MISSING,
            view=view_class(self.bot, lines, egg, container, vfile, vlink),
            ephemeral=True
        )

    @app.command(name="report", description="report_description")
    @app.rename(id="report_id")
    @app.describe(id="report_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def report(self, ctx: discord.Interaction, id: int):
        await self._confirm_flow(ctx, "eggs/report", id, views.PreReportEgg)

    @app.command(name="delete", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def delete(self, ctx: discord.Interaction, id: int):
        await self._confirm_flow(ctx, "eggs/delete", id, views.DeleteEgg, check_manage=True)
    
    @app.command(name="crack", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def crack(self, ctx: discord.Interaction, id: int):
        await self._confirm_flow(ctx, "eggs/delete", id, views.DeleteEgg, check_manage=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggs(bot))