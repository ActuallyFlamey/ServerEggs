import discord
from discord import app_commands as app
from discord.ext import commands

from schema import Guild, User


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
            lines = await self.bot.fetch_lines(ctx)
            myloc = self.bot.get_lines("config/lang", lines)

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

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("config/lang", lines)

        await ctx.followup.send(myloc["success"], ephemeral=True)

    @app.command(name="allow-user-lang", description="allow-user-lang_description")
    @app.rename(allow="allow-user-lang_allow")
    @app.describe(allow="allow-user-lang_allow_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def allow_user_lang(self, ctx: discord.Interaction, allow: bool):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("config/allow-user-lang", lines)

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

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("config/server-description", lines)

        guild, _ = await Guild.update_or_create({ "description": desc }, id=ctx.guild.id)

        await ctx.followup.send(content=myloc["success"].format(guild.description), ephemeral=True)

    @app.command(name="privacy", description="privacy_description")
    @app.rename(private="privacy_private")
    @app.describe(private="privacy_private_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app.checks.has_permissions(manage_guild=True)
    async def privacy(self, ctx: discord.Interaction, private: bool):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("config/privacy", lines)

        guild = await Guild.get_or_none(id=ctx.guild.id)
        has_invite = bool(guild.invite)

        if (has_invite and not private) or (not has_invite and private):
            await ctx.followup.send(content=myloc["already"], ephemeral=True)
            return

        invite = None
        if not private:
            inviteobj = await ctx.guild.rules_channel.create_invite() if ctx.guild.rules_channel else await ctx.guild.text_channels[0].create_invite()
            invite = inviteobj.url

        guild.invite = invite
        await guild.save(update_fields=["invite"])

        await ctx.followup.send(content=myloc["success"].format(private), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))