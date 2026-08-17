from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0004_feat_filtered_eggs_on_guild')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Report',
            name='related_message_id',
            field=fields.BigIntField(null=True),
        )
    ]
