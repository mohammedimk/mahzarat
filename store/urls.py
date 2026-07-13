from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [
    # ----- Public storefront -----
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_view, name='search'),

    # ----- Admin panel (custom, professional interface) -----
    path('admin-panel/register/', views.admin_register, name='admin_register'),
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/products/add/', views.add_product, name='add_product'),
    path('admin-panel/products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('admin-panel/products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('admin-panel/settings/', views.admin_settings, name='admin_settings'),

    # --- Checkout & Payment Flow ---
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<str:order_id>/', views.payment, name='payment'),
    path('payment/<str:order_id>/success/', views.payment_success, name='payment_success'),
    path('order/<str:order_id>/status/', views.order_status, name='order_status'),
    path('admin-panel/bank/', views.manage_bank_account, name='manage_bank_account'),
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/bank/delete/', views.delete_bank_account, name='delete_bank_account'),
    # Add this line right below your other admin/order routes
    path('admin-panel/orders/update-shipping/', views.admin_update_shipping, name='admin_update_shipping'),

    path('login/', views.customer_login, name='customer_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),



]
