from tortoise.functions import Count

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

def format_count(count: int) -> str:
    return f"{count:_}".replace("_", " ")

class Leaderboard:
    def __init__(self, model, field, *, limit: int = 15):
        self.model = model
        self.field = field
        self.limit = limit

    def _base(self):
        return self.model.annotate(egg_count=Count(self.field))

    async def top(self):
        return await self._base().order_by("-egg_count").limit(self.limit).values("id", "egg_count")

    async def rank_of(self, entity_id: int) -> tuple[int, int]:
        rows = await self._base().filter(id=entity_id).values("egg_count")
        count = rows[0]["egg_count"] if rows else 0
        higher = await self._base().filter(egg_count__gt=count).count()
        return higher + 1, count

async def render_entries(bot, leaderboard: Leaderboard, self_id: int, name_resolver, self_suffix: str = "") -> list[str]:
    top = await leaderboard.top()
    rank, count = await leaderboard.rank_of(self_id)

    async def row(index: int, entity_id: int, entity_count: int, *, self_row: bool) -> str:
        name = await name_resolver(bot, entity_id)
        prefix = MEDALS.get(index, f"`{index}`")
        marker = "*" if self_row else ""
        suffix = self_suffix if self_row else ""
        return f"{marker}{prefix} — {name}{suffix} — {format_count(entity_count)}{marker}"

    entries = [
        await row(index, entry["id"], entry["egg_count"], self_row=entry["id"] == self_id)
        for index, entry in enumerate(top, start=1)
    ]

    if not any(entry["id"] == self_id for entry in top):
        entries.append(await row(rank, self_id, count, self_row=True))

    return entries