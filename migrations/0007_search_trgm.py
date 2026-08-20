from tortoise import migrations
from tortoise.migrations import operations as ops


class RawSQLOperation(ops.Operation):
    reversible = True

    def __init__(self, forward: str, backward: str | None = None):
        self.forward = forward
        self.backward = backward

    def describe(self) -> str:
        return f"RawSQL: {self.forward}"

    def state_forward(self, app_label, state) -> None:
        return None

    async def database_forward(self, app_label, old_state, new_state, state_editor=None):
        if state_editor:
            await state_editor._run_sql(self.forward)

    async def database_backward(self, app_label, old_state, new_state, state_editor=None):
        if state_editor and self.backward:
            await state_editor._run_sql(self.backward)


class Migration(migrations.Migration):
    dependencies = [('eggs', '0006_feat_remove_related_reports_add_method_for_egg')]

    initial = False

    operations = [
        RawSQLOperation(
            'CREATE EXTENSION IF NOT EXISTS pg_trgm',
            'DROP EXTENSION IF EXISTS pg_trgm',
        ),
        RawSQLOperation(
            'CREATE INDEX IF NOT EXISTS idx_egg_text_trgm ON egg USING gin (text gin_trgm_ops)',
            'DROP INDEX IF EXISTS idx_egg_text_trgm',
        ),
    ]