from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_update_categories'),  
    ]

    operations = [
        # 1. Automatically inject structural tables directly into Render's PostgreSQL database
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS store_bankaccount (
                id SERIAL PRIMARY KEY,
                bank_name VARCHAR(100) NOT NULL,
                account_name VARCHAR(150) NOT NULL,
                account_number VARCHAR(20) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS store_order (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(50) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                customer_name VARCHAR(150) NOT NULL,
                customer_email VARCHAR(254) NOT NULL,
                customer_phone VARCHAR(20) NOT NULL,
                cart_items JSONB NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE NULL
            );
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS store_bankaccount;
            DROP TABLE IF EXISTS store_order;
            """
        ),
        
        # 2. Map structural components to your Django Model Registry
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=100)),
                ('account_name', models.CharField(max_length=150)),
                ('account_number', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Bank Accounts',
                'managed': False, 
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Payment'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('customer_name', models.CharField(max_length=150)),
                ('customer_email', models.EmailField(max_length=254)),
                ('customer_phone', models.CharField(max_length=20)),
                ('cart_items', models.JSONField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'managed': False, 
            },
        ),
    ]
