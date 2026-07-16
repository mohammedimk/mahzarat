from django.db import migrations


def add_new_categories(apps, schema_editor):
    """Add Crypto and Others categories"""
    Category = apps.get_model('store', 'Category')
    
    new_categories = [
        ('Crypto', 'crypto'),
        ('Others', 'others'),
    ]
    
    for name, slug in new_categories:
        Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name}
        )


def reverse(apps, schema_editor):
    """Remove Crypto and Others categories"""
    Category = apps.get_model('store', 'Category')
    Category.objects.filter(slug__in=['crypto', 'others']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', ''),
    ]

    operations = [
        migrations.RunPython(add_new_categories, reverse),
    ]
