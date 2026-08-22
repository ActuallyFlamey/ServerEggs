from tortoise import fields, migrations
from tortoise.fields.base import OnDelete
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [("eggs", "0012_feat_battle_time_on_guild")]

    initial = False

    operations = [
        ops.AlterField(
            model_name="Egg",
            name="creator",
            field=fields.ForeignKeyField("eggs.User", source_field="creator_id", null=True, db_constraint=True, to_field="id", related_name="eggs", on_delete=OnDelete.SET_NULL),
        ),
        ops.AlterField(
            model_name="Egg",
            name="origin",
            field=fields.ForeignKeyField("eggs.Guild", source_field="origin_id", null=True, db_constraint=True, to_field="id", related_name="eggs", on_delete=OnDelete.SET_NULL),
        ),
    ]
