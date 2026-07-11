

from django.contrib import admin
from .models import Category, Product, SiteSetting, BankAccount, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'status', 'is_featured', 'views', 'created_at')
    list_filter = ('category', 'status', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


# =====================================================================
# BANK ACCOUNT ADMIN - For payment system
# =====================================================================

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """
    Admin interface for managing bank account details.
    Allows adding and editing the bank account customers transfer to.
    """
    list_display = ('bank_name', 'account_name', 'account_number', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('bank_name', 'account_name', 'account_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Bank Information', {
            'fields': ('bank_name', 'account_name', 'account_number')
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Check this box to make this account active for customer payments'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# =====================================================================
# ORDER ADMIN - For tracking customer orders
# =====================================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing customer orders.
    Shows payment status, customer details, and order contents.
    """
    list_display = ('order_id', 'customer_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_id', 'created_at', 'cart_items')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Order Contents', {
            'fields': ('cart_items', 'total_amount')
        }),
    )
    
    def has_delete_permission(self, request):
        """Prevent accidental deletion of orders"""
        return False









