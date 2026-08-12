from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0002_feat_collecting')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Guild',
            name='logch',
            field=fields.BigIntField(null=True),
        )
    ]
