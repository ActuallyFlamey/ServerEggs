import discord
from discord.ext import commands

import utils
from schema import BattleStatus, BattleVote, User


class BattleView(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, battle, sides: list[dict]):
        super().__init__(timeout=None)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("battles/battle", lines)
        self.battle = battle
        self.sides = sides

        self.vote_a.label = self.myloc["vote"].format("A")
        self.vote_b.label = self.myloc["vote"].format("B")

        for side_index, button_name in ((0, "show_a"), (1, "show_b")):
            button = getattr(self, button_name)
            side = self.sides[side_index]

            if side["vfile"] or side["vlink"]:
                button.label = self.myloc["show"].format(button_name.split("_")[-1].upper())
            else:
                self.remove_item(button)

    async def interaction_check(self, ctx: discord.Interaction):
        if self.battle.status != BattleStatus.OPEN:
            await ctx.response.send_message(self.myloc["ended"], ephemeral=True)
            return False

        return True

    async def vote(self, ctx: discord.Interaction, choice: int):
        voter, _ = await User.get_or_create(id=ctx.user.id)

        if voter.banned:
            await ctx.response.send_message(self.myloc["banned"], ephemeral=True)
            return

        await BattleVote.update_or_create(battle=self.battle, voter=voter, defaults={"choice": choice})

        count_a, count_b = await utils.count_votes(self.battle)

        self.vote_a.label = f"{self.myloc["vote"].format("A")} ({count_a})"
        self.vote_b.label = f"{self.myloc["vote"].format("B")} ({count_b})"

        await ctx.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def vote_a(self, ctx: discord.Interaction, button: discord.ui.Button):
        await self.vote(ctx, 0)

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def vote_b(self, ctx: discord.Interaction, button: discord.ui.Button):
        await self.vote(ctx, 1)

    @discord.ui.button(style=discord.ButtonStyle.secondary, row=1)
    async def show_a(self, ctx: discord.Interaction, button: discord.ui.Button):
        await utils.send_extra(ctx, self.sides[0]["vfile"], self.sides[0]["vlink"])

    @discord.ui.button(style=discord.ButtonStyle.secondary, row=1)
    async def show_b(self, ctx: discord.Interaction, button: discord.ui.Button):
        await utils.send_extra(ctx, self.sides[1]["vfile"], self.sides[1]["vlink"])

class ChallengeView(discord.ui.View):
    def __init__(self, bot: commands.Bot, lines: dict, prompt: discord.Message, challenger: discord.User, challenged: discord.User, egg):
        super().__init__(timeout=3600)

        self.bot = bot
        self.lines = lines
        self.myloc = bot.get_lines("battles/challenge", lines)
        self.prompt = prompt
        self.challenger = challenger
        self.challenged = challenged
        self.egg = egg
        self.done = False

        self.accept.label = self.myloc["accept"]
        self.decline.label = self.myloc["decline"]

    async def interaction_check(self, ctx: discord.Interaction):
        if ctx.user.id != self.challenged.id:
            await ctx.response.send_message(self.myloc["not_yours"], ephemeral=True)
            return False

        return True

    async def on_timeout(self):
        if self.done:
            return

        try:
            await self.prompt.edit(content=self.myloc["expired"], view=None)
        except discord.HTTPException:
            pass

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def accept(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.done = True

        await ctx.response.send_modal(ChallengeModal(self.bot, self.lines, self.prompt, self.challenger, self.challenged, self.egg))

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def decline(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.done = True

        await ctx.response.edit_message(content=self.myloc["declined"], view=None)

class ChallengeModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, lines: dict, prompt: discord.Message, challenger: discord.User, challenged: discord.User, egg):
        self.bot = bot
        self.myloc = bot.get_lines("battles/challenge", lines)
        self.prompt = prompt
        self.challenger = challenger
        self.challenged = challenged
        self.egg = egg

        super().__init__(title=self.myloc["modal_title"])

        self.egg_id = discord.ui.TextInput(
            label=self.myloc["modal_id"],
            placeholder=self.myloc["modal_id_placeholder"],
            required=False,
            max_length=10
        )

        self.add_item(self.egg_id)

    async def on_submit(self, ctx: discord.Interaction):
        cog = self.bot.get_cog("Battles")

        await cog.accept_challenge(ctx, self.prompt, self.challenger, self.challenged, self.egg, self.egg_id.value)