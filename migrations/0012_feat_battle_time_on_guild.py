from tortoise import migrations
from tortoise.migrations import operations as ops
import datetime
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0011_feat_user_battle_wins')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Guild',
            name='battle_time',
            field=fields.TimeDeltaField(default=datetime.timedelta(seconds=600.0), null=True),
        ),
        ops.RunSQL(
            sql="""
                UPDATE guild
                SET battle_time = 900000000
                WHERE battle_time IS NULL;
            """
        ),
        ops.AlterField(
            model_name='Guild',
            name='battle_time',
            field=fields.TimeDeltaField(default=datetime.timedelta(seconds=600.0), null=False)
        )
    ]
