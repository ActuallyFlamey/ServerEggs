from tortoise import fields, migrations
from tortoise.fields.base import OnDelete
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [("eggs", "0010_feat_battles")]

    initial = False

    operations = [
        ops.AddField(
            model_name="Battle",
            name="winner_user",
            field=fields.ForeignKeyField("eggs.User", source_field="winner_user_id", null=True, db_constraint=True, to_field="id", related_name="user_battle_wins", on_delete=OnDelete.CASCADE),
        ),
    ]
