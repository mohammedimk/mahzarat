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
]
