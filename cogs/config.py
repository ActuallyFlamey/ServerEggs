import discord
from discord import app_commands as app
from discord.ext import commands

from schema import Guild, Rating, User, default_ratings


class Config(commands.GroupCog, group_name="config", group_description="config_description"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app.command(name="lang", description="lang_description")
    @app.rename(code="lang_language")
    @app.describe(code="lang_language_description")
    @app.choices(code=[
        app.Choice(name=app.locale_str("lang_default"), value=""),
        app.Choice(name="English", value="en"),
        app.Choice(name="Italiano", value="it"),
    ])
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def lang(self, ctx: discord.Interaction, code: str):
        await ctx.response.defer(ephemeral=True)

        if ctx.guild:
            _, myloc = await self.bot.get_section(ctx, "config/lang")

            if code == "":
                await ctx.followup.send(myloc["no_default"], ephemeral=True)
                return

            if not ctx.permissions.manage_guild:
                await ctx.followup.send(myloc["no_permissions"], ephemeral=True)
                return
            else:
                await Guild.update_or_create(defaults={ "lang": code }, id=ctx.guild.id)
                self.bot.lang_cache[f"guild_{ctx.guild.id}"] = code
        else:
            await User.update_or_create(defaults={ "lang": code }, id=ctx.user.id)
            self.bot.lang_cache[f"user_{ctx.user.id}"] = code

        _, myloc = await self.bot.get_section(ctx, "config/lang")

        await ctx.followup.send(myloc["success"], ephemeral=True)

    @app.command(name="allow-user-lang", description="allow-user-lang_description")
    @app.rename(allow="allow-user-lang_allow")
    @app.describe(allow="allow-user-lang_allow_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def allow_user_lang(self, ctx: discord.Interaction, allow: bool):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/allow-user-lang")

        cache_key = f"guild_{ctx.guild.id}_allowuserlang"

        if self.bot.lang_cache[cache_key] == allow:
            await ctx.followup.send(myloc["already"], ephemeral=True)
            return

        guild, _ = await Guild.update_or_create(defaults={ "allow_user_lang": allow }, id=ctx.guild.id)
        self.bot.lang_cache[cache_key] = guild.allow_user_lang

        await ctx.followup.send(myloc["success"].format(allow), ephemeral=True)

    @app.command(name="server-description", description="server-description_description")
    @app.rename(desc="server-description_desc")
    @app.describe(desc="server-description_desc_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def server_description(self, ctx: discord.Interaction, desc: str):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/server-description")

        guild, _ = await Guild.update_or_create({ "description": desc }, id=ctx.guild.id)

        await ctx.followup.send(myloc["success"] + "\n" + guild.description, ephemeral=True)

    @app.command(name="privacy", description="privacy_description")
    @app.rename(public="privacy_public")
    @app.describe(public="privacy_public_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def privacy(self, ctx: discord.Interaction, public: bool):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/privacy")

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        has_invite = bool(guild.invite)

        if (has_invite and public) or (not has_invite and not public):
            await ctx.followup.send(myloc["already"], ephemeral=True)
            return

        invite = None
        if public:
            try:
                inviteobj = await ctx.guild.rules_channel.create_invite() if ctx.guild.rules_channel else await ctx.guild.text_channels[0].create_invite()
                invite = inviteobj.url
            except discord.errors.Forbidden:
                await ctx.followup.send(myloc["missing_perms"], ephemeral=True)
                return

        guild.invite = invite
        await guild.save(update_fields=["invite"])

        await ctx.followup.send(myloc["success"].format(public), ephemeral=True)

    @app.command(name="log", description="log_description")
    @app.rename(channel="log_channel")
    @app.describe(channel="log_channel_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def log(self, ctx: discord.Interaction, channel: discord.TextChannel):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/log")

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if channel.id == guild.logch:
            await ctx.followup.send(myloc["already"], ephemeral=True)
            return

        perms = channel.permissions_for(ctx.guild.me)
        if not (perms.view_channel and perms.send_messages and perms.embed_links):
            await ctx.followup.send(myloc["missing_perms"], ephemeral=True)
            return

        guild.logch = channel.id
        await guild.save(update_fields=["logch"])

        await ctx.followup.send(myloc["success"].format(channel.mention), ephemeral=True)

    allowed_ratings = app.Group(
        name="allowed-ratings",
        description="allowed-ratings_description",
        allowed_contexts=app.AppCommandContext(guild=True, dm_channel=False, private_channel=False)
    )

    async def set_allowed_ratings(self, ctx: discord.Interaction, group: str, safe: bool | None, questionable: bool | None, explicit: bool | None):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/allowed-ratings")

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        changes = {
            Rating.SAFE: safe,
            Rating.QUESTIONABLE: questionable,
            Rating.EXPLICIT: explicit,
        }

        if all(value is None for value in changes.values()):
            await ctx.followup.send(myloc["no_changes"], ephemeral=True)
            return

        if group == "normal" and changes[Rating.EXPLICIT] is True:
            await ctx.followup.send(myloc["no_explicit_in_normal"], ephemeral=True)
            return

        if not guild.ratings:
            guild.ratings = default_ratings()

        setting = set(guild.ratings.get(group, []))

        for rating, value in changes.items():
            if value is None:
                continue

            if value:
                setting.add(rating)
            else:
                setting.discard(rating)

        setting = [rating for rating in (Rating.SAFE, Rating.QUESTIONABLE, Rating.EXPLICIT) if rating in setting]

        if guild.ratings.get(group) == setting:
            await ctx.followup.send(myloc["already"], ephemeral=True)
            return

        guild.ratings[group] = setting
        await guild.save(update_fields=["ratings"])

        await ctx.followup.send(myloc["success"], ephemeral=True)

    @allowed_ratings.command(name="allowed-ratings_normal", description="allowed-ratings_normal_description")
    @app.rename(safe="allowed-ratings_normal_s", questionable="allowed-ratings_normal_q", explicit="allowed-ratings_normal_e")
    @app.describe(safe="allowed-ratings_normal_s_description", questionable="allowed-ratings_normal_q_description", explicit="allowed-ratings_normal_e_description")
    @app.checks.has_permissions(manage_guild=True)
    async def allowed_ratings_normal(self, ctx: discord.Interaction, safe: bool | None, questionable: bool | None, explicit: bool | None):
        await self.set_allowed_ratings(ctx, "normal", safe, questionable, explicit)

    @allowed_ratings.command(name="allowed-ratings_nsfw", description="allowed-ratings_nsfw_description")
    @app.rename(safe="allowed-ratings_nsfw_s", questionable="allowed-ratings_nsfw_q", explicit="allowed-ratings_nsfw_e")
    @app.describe(safe="allowed-ratings_nsfw_s_description", questionable="allowed-ratings_nsfw_q_description", explicit="allowed-ratings_nsfw_e_description")
    @app.checks.has_permissions(manage_guild=True)
    async def allowed_ratings_nsfw(self, ctx: discord.Interaction, safe: bool | None, questionable: bool | None, explicit: bool | None):
        await self.set_allowed_ratings(ctx, "nsfw", safe, questionable, explicit)
    
    @app.command(name="join-button", description="join-button_description")
    @app.rename(viewable="join-button_viewable")
    @app.describe(viewable="join-button_viewable_description")
    @app.checks.has_permissions(manage_guild=True)
    async def join_button(self, ctx: discord.Interaction, viewable: bool):
        await ctx.response.defer(ephemeral=True)

        _, myloc = await self.bot.get_section(ctx, "config/join-button")

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if guild.view_join_button == viewable:
            await ctx.followup.send(myloc["already"], ephemeral=True)
            return
        
        guild.view_join_button = viewable
        await guild.save(update_fields=["view_join_button"])

        await ctx.followup.send(myloc["success"].format(viewable), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))