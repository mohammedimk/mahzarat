from django.db import migrations


def update_categories(apps, schema_editor):
    """Automatically update categories on deploy"""
    Category = apps.get_model('store', 'Category')
    Product = apps.get_model('store', 'Product')
    
    # Create new categories
    new_categories = [
        ('Captans', 'captans'),
        ('Caps', 'caps'),
        ('Jeans/Shirt', 'jeansshirt'),
        ('Blouse', 'blouse'),
        ('Shoes', 'shoes'),
        ('Skirt', 'skirt'),
        ('Scarfs', 'scarfs'),
        ('Hijabs', 'hijabs'),
        ('Textiles', 'textiles'),
        ('Shedda', 'shedda'),
        ('Gatzner', 'gatzner'),
    ]
    
    for name, slug in new_categories:
        Category.objects.get_or_create(slug=slug, defaults={'name': name})
    
    # Move products from old categories to Captans
    try:
        captans = Category.objects.get(slug='captans')
        old_slugs = ['dresses', 'ankara', 'coord', 'outerwear', 'accessories']
        
        for old_slug in old_slugs:
            try:
                old_cat = Category.objects.get(slug=old_slug)
                Product.objects.filter(category=old_cat).update(category=captans)
                old_cat.delete()
            except Category.DoesNotExist:
                pass
    except Category.DoesNotExist:
        pass


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_sitesetting_hero_subtitle'),  # <- THIS LINE CHANGED
    ]

    operations = [
        migrations.RunPython(update_categories, reverse),
    ]
