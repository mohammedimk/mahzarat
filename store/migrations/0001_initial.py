from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    starter = [
        ('Dresses', 'dresses'),
        ('Ankara & Prints', 'ankara'),
        ('Co-ord Sets', 'coord'),
        ('Outerwear', 'outerwear'),
        ('Accessories', 'accessories'),
    ]
    for name, slug in starter:
        Category.objects.get_or_create(slug=slug, defaults={'name': name})


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Category.objects.filter(
        slug__in=['dresses', 'ankara', 'coord', 'outerwear', 'accessories']
    ).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SiteSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(default="Dress for the life you're actually living.", max_length=200)),
                ('hero_subtitle', models.CharField(blank=True, default='Botokhan Store designs everyday clothing for women who refuse to choose between comfort and presence.', max_length=300)),
                ('hero_image', models.ImageField(blank=True, null=True, upload_to='site/')),
                ('lookbook_image_1', models.ImageField(blank=True, null=True, upload_to='site/')),
                ('lookbook_image_2', models.ImageField(blank=True, null=True, upload_to='site/')),
            ],
            options={
                'verbose_name': 'Site Setting',
                'verbose_name_plural': 'Site Settings',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(upload_to='products/')),
                ('tag', models.CharField(blank=True, choices=[('', 'None'), ('New', 'New'), ('Best seller', 'Best seller'), ('Trending', 'Trending'), ('Sale', 'Sale')], default='', max_length=30)),
                ('sizes', models.CharField(blank=True, default='', help_text='Comma-separated, e.g. XS,S,M,L,XL — use "One Size" for accessories.', max_length=150)),
                ('colors', models.CharField(blank=True, default='', help_text='Comma-separated hex codes, e.g. #1F4436,#B08D57,#C98FA1', max_length=200)),
                ('status', models.CharField(choices=[('active', 'Active (visible on store)'), ('inactive', 'Inactive (hidden)')], default='active', max_length=10)),
                ('is_featured', models.BooleanField(default=False, help_text="Spotlight in Editor's Picks on the homepage")),
                ('views', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(seed_categories, unseed_categories),
    ]
