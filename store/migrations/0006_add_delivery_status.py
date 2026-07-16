from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_customerprofile'),  # Make sure this matches your last migration
    ]

    operations = [
        # Alter the actual PostgreSQL table on Render
        migrations.RunSQL(
            sql="""
            ALTER TABLE store_order ADD COLUMN IF NOT EXISTS is_delivered BOOLEAN DEFAULT FALSE;
            ALTER TABLE store_order ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP WITH TIME ZONE NULL;
            """,
            reverse_sql="""
            ALTER TABLE store_order DROP COLUMN IF EXISTS is_delivered;
            ALTER TABLE store_order DROP COLUMN IF EXISTS delivered_at;
            """
        ),
    ]
