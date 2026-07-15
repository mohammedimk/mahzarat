# Generated manually for Render database deployment
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # This makes sure it runs directly after your payment system migration
        ('store', '0004_payment_system'),  
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('billing_address', models.CharField(blank=True, max_length=255, null=True)),
                ('billing_city', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_state', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_zip', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer Profile',
                'verbose_name_plural': 'Customer Profiles',
            },
        ),
    ]
