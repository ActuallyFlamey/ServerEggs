from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0008_feat_ratings')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Guild',
            name='view_join_button',
            field=fields.BooleanField(default=True, null=True),
        ),
        ops.RunSQL(
            sql="""
                UPDATE "guild"
                SET view_join_button = true;
            """
        ),
        ops.AlterField(
            model_name='Guild',
            name='view_join_button',
            field=fields.BooleanField(default=True, null=False)
        )
    ]
