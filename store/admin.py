from django.contrib import admin
# Imported BankAccount and Order alongside your existing models
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
# NEW REGISTRATIONS
# =====================================================================

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    # Displays clean columns in the admin portal list layout
    list_display = ('bank_name', 'account_name', 'account_number', 'is_active')
    # Professional touch: lets you toggle an account active/inactive without opening it
    list_editable = ('is_active',)
    list_filter = ('is_active',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_id', 'created_at') # Keeps order numbers and timestamps safe from manual typos
