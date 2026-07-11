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

# >>> ADD THIS TO store/models.py AT THE END <<<

from django.db import models
from django.utils import timezone


class BankAccount(models.Model):
    """
    Store bank transfer details (account number, bank name, account holder).
    Only one active bank account at a time (for simplicity).
    Admin sets this up once in Django admin.
    """
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        return f'{self.bank_name} - {self.account_name} ({self.account_number})'

    @classmethod
    def get_active(cls):
        """Get the currently active bank account"""
        return cls.objects.filter(is_active=True).first()


class Order(models.Model):
    """
    Customer order - tracks what they're buying and how much they need to pay.
    Status: pending (waiting for payment) → completed (paid) → cancelled
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Order tracking
    order_id = models.CharField(max_length=50, unique=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Customer info
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Cart details (stored as JSON since it's variable)
    cart_items = models.JSONField()  # list of {id, name, price, size, qty}
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_id} - {self.customer_name} ({self.status})'

    def mark_completed(self):
        """Mark this order as successfully paid"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel this order"""
        self.status = 'cancelled'
        self.save()

