from schema import BattleStatus
from tortoise import fields, migrations
from tortoise.fields.base import OnDelete
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [("eggs", "0009_feat_view_join_button_on_guild")]

    initial = False

    operations = [
        ops.CreateModel(
            name="Battle",
            fields=[
                ("id", fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ("channel_id", fields.BigIntField(null=True, unique=False)),
                ("message_id", fields.BigIntField(null=True, unique=False)),
                ("ends_at", fields.DatetimeField(db_index=True)),
                ("status", fields.CharEnumField(
                    enum_type=BattleStatus,
                    max_length=10,
                    default=BattleStatus.OPEN,
                    description="OPEN: OPEN\nFINISHED: FINISHED",
                )),
                ("guild", fields.ForeignKeyField("eggs.Guild", source_field="guild_id", db_constraint=True, to_field="id", related_name="battles", on_delete=OnDelete.CASCADE)),
                ("egg_a", fields.ForeignKeyField("eggs.Egg", source_field="egg_a_id", db_constraint=True, to_field="id", related_name="battles_as_a", on_delete=OnDelete.CASCADE)),
                ("egg_b", fields.ForeignKeyField("eggs.Egg", source_field="egg_b_id", db_constraint=True, to_field="id", related_name="battles_as_b", on_delete=OnDelete.CASCADE)),
                ("user_a", fields.ForeignKeyField("eggs.User", source_field="user_a_id", null=True, db_constraint=True, to_field="id", related_name="challenges_sent", on_delete=OnDelete.CASCADE)),
                ("user_b", fields.ForeignKeyField("eggs.User", source_field="user_b_id", null=True, db_constraint=True, to_field="id", related_name="challenges_received", on_delete=OnDelete.CASCADE)),
                ("winner", fields.ForeignKeyField("eggs.Egg", source_field="winner_id", null=True, db_constraint=True, to_field="id", related_name="battle_wins", on_delete=OnDelete.CASCADE)),
            ],
            options={"table": "battle", "app": "eggs", "pk_attr": "id"},
            bases=["Model"],
        ),
        ops.CreateModel(
            name="BattleVote",
            fields=[
                ("id", fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ("choice", fields.IntField()),
                ("battle", fields.ForeignKeyField("eggs.Battle", source_field="battle_id", db_constraint=True, to_field="id", related_name="votes", on_delete=OnDelete.CASCADE)),
                ("voter", fields.ForeignKeyField("eggs.User", source_field="voter_id", db_constraint=True, to_field="id", related_name="battle_votes", on_delete=OnDelete.CASCADE)),
            ],
            options={"table": "battle_vote", "app": "eggs", "unique_together": (("battle", "voter"),), "pk_attr": "id"},
            bases=["Model"],
        ),
    ]
