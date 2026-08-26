from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0014_feat_private_on_user')]

    initial = False

    operations = [
        ops.RenameField(
            model_name='User',
            old_name='private',
            new_name='public',
        ),
        ops.RunSQL(sql="""
            UPDATE "user"
            SET public = true
            WHERE public = false
        """)
    ]
