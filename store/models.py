from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active (visible on store)'),
        ('inactive', 'Inactive (hidden)'),
    ]
    TAG_CHOICES = [
        ('', 'None'),
        ('New', 'New'),
        ('Best seller', 'Best seller'),
        ('Trending', 'Trending'),
        ('Sale', 'Sale'),
    ]

    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/')
    tag = models.CharField(max_length=30, choices=TAG_CHOICES, blank=True, default='')
    sizes = models.CharField(
        max_length=150, blank=True, default='',
        help_text='Comma-separated, e.g. XS,S,M,L,XL — use "One Size" for accessories.'
    )
    colors = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Comma-separated hex codes, e.g. #1F4436,#B08D57,#C98FA1'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False, help_text="Spotlight in Editor's Picks on the homepage")
    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'product'
            slug = base
            i = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def sizes_list(self):
        return [s.strip() for s in self.sizes.split(',') if s.strip()]

    def colors_list(self):
        return [c.strip() for c in self.colors.split(',') if c.strip()]


class SiteSetting(models.Model):
    """
    A one-row "singleton" table so the admin can edit the homepage hero and
    lookbook photos/text from the dashboard, without touching any code.
    """
    hero_title = models.CharField(
        max_length=200,
        default="Dress for the life you're actually living."
    )
    hero_subtitle = models.CharField(
        max_length=300, blank=True,
        default="Mahzarat Store designs everyday clothing for women who refuse "
                "to choose between comfort and presence."
    )
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    lookbook_image_1 = models.ImageField(upload_to='site/', blank=True, null=True)
    lookbook_image_2 = models.ImageField(upload_to='site/', blank=True, null=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
