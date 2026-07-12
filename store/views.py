import json
import uuid
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 🚀 Make sure BankAccountForm and an OrderForm/representation are available if needed
from .forms import AdminLoginForm, AdminRegisterForm, ProductForm, SiteSettingForm
from .models import Category, Product, SiteSetting, BankAccount, Order

PER_PAGE = 9


def product_to_dict(product):
    """Small JSON-serializable representation of a product, used to power
    the client-side cart and quick-view modal without extra page loads."""
    return {
        'id': product.pk,
        'name': product.name,
        'slug': product.slug,
        'category': product.category.name,
        'price': float(product.price),
        'old_price': float(product.old_price) if product.old_price else None,
        'description': product.description,
        'image': product.image.url if product.image else '',
        'tag': product.tag,
        'sizes': product.sizes_list() or ['One Size'],
        'colors': product.colors_list(),
    }


# =====================================================================
# PUBLIC STOREFRONT
# =====================================================================

def index(request):
    settings_obj = SiteSetting.load()
    categories = Category.objects.all()

    active_products = Product.objects.filter(status='active').select_related('category')
    featured = active_products.filter(is_featured=True).first() or active_products.first()

    grid_qs = active_products.exclude(pk=featured.pk) if featured else active_products
    paginator = Paginator(grid_qs, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    popular = active_products.order_by('-views')[:5]

    # 🚀 OPTIMIZATION: Resolve N+1 query problem by pulling latest updates in a batch query
    recent_products = Product.objects.filter(status='active').order_by('-created_at')
    category_thumbs = {}
    for cat in categories:
        thumb = recent_products.filter(category=cat).first()
        category_thumbs[cat.id] = thumb

    products_json = [product_to_dict(p) for p in page_obj.object_list]

    return render(request, 'store/index.html', {
        'settings_obj': settings_obj,
        'categories': categories,
        'featured': featured,
        'page_obj': page_obj,
        'popular': popular,
        'category_thumbs': category_thumbs,
        'products_json': products_json,
        'active_nav': 'home',
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, status='active').order_by('-created_at')

    paginator = Paginator(products, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    products_json = [product_to_dict(p) for p in page_obj.object_list]

    return render(request, 'store/category.html', {
        'category': category,
        'page_obj': page_obj,
        'products_json': products_json,
        'active_nav': 'category',
        'active_category_slug': category.slug,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='active')

    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
    product.refresh_from_db()

    related = Product.objects.filter(
        category=product.category, status='active'
    ).exclude(pk=product.pk)[:4]

    combined_json = [product_to_dict(product)] + [product_to_dict(p) for p in related]

    return render(request, 'store/product.html', {
        'product': product,
        'related': related,
        'products_json': combined_json,
        'active_category_slug': product.category.slug,
    })


def search_view(request):
    query = request.GET.get('q', '').strip()
    page_obj = None
    products_json = []

    if query:
        results = Product.objects.filter(status='active').filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(results, PER_PAGE)
        page_obj = paginator.get_page(request.GET.get('page'))
        products_json = [product_to_dict(p) for p in page_obj.object_list]

    return render(request, 'store/search.html', {
        'query': query,
        'page_obj': page_obj,
        'products_json': products_json,
    })


@require_http_methods(["POST"])
@csrf_exempt
def checkout(request):
    """
    >>> CHECKOUT PAGE <<<
    User submits cart details and personal info.
    Creates an Order record and redirects to payment page.
    """
    try:
        cart_json = request.POST.get('cart_json', '[]')
        cart = json.loads(cart_json)

        if not cart:
            messages.error(request, 'Your cart is empty.')
            return redirect('store:index')

        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()

        if not customer_name or not customer_email or not customer_phone:
            messages.error(request, 'Please fill in all required fields correctly.')
            return redirect('store:index')

        total_amount = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart)

        date_str = timezone.now().strftime('%y%m%d') 
        uuid_str = str(uuid.uuid4())[:6].upper()      
        order_id = f"ORD-{date_str}-{uuid_str}"

        order = Order.objects.create(
            order_id=order_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            cart_items=cart,
            total_amount=total_amount,
        )

        return redirect('store:payment', order_id=order.order_id)

    except Exception as e:
        messages.error(request, f'Checkout error: {str(e)}')
        return redirect('store:index')


def payment(request, order_id):
    """
    >>> PAYMENT PAGE <<<
    Display bank transfer instructions and amount to pay.
    """
    try:
        order = get_object_or_404(Order, order_id=order_id, status='pending')
        
        if hasattr(BankAccount, 'get_active'):
            bank = BankAccount.get_active()
        else:
            bank = BankAccount.objects.filter(is_active=True).first()

        if not bank:
            messages.error(request, 'Bank details not configured. Please contact support.')
            return redirect('store:index')

        return render(request, 'store/payment.html', {
            'order': order,
            'bank': bank,
            'currency_symbol': '₦',
        })

    except Exception as e:
        messages.error(request, f'Error loading payment page: {str(e)}')
        return redirect('store:index')


def payment_success(request, order_id):
    try:
        order = get_object_or_404(Order, order_id=order_id)
        return render(request, 'store/payment_success.html', {
            'order': order,
            'currency_symbol': '₦',
        })
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('store:index')


def order_status(request, order_id):
    try:
        order = get_object_or_404(Order, order_id=order_id)
        return render(request, 'store/order_status.html', {
            'order': order,
            'currency_symbol': '₦',
        })
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('store:index')


# =====================================================================
# ADMIN PANEL
# =====================================================================

def admin_register(request):
    """Register new admin user - automatically make them superuser"""
    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
                
            messages.success(request, 'Admin account created successfully! You are now a superuser.')
            return redirect('store:admin_login')
    else:
        form = AdminRegisterForm()
    
    return render(request, 'store/admin/register.html', {'form': form})


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('store:admin_dashboard')

    form = AdminLoginForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['username'].strip()
        password = form.cleaned_data['password']

        username = identifier
        if '@' in identifier:
            try:
                username = User.objects.get(email__iexact=identifier).username
            except User.DoesNotExist:
                username = identifier

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('store:admin_dashboard')
            else:
                error = 'Access Denied: Your account does not have staff permissions.'
        else:
            error = 'Incorrect username/email or password.'

    return render(request, 'store/admin/login.html', {'form': form, 'error': error})


def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:admin_login')


@login_required(login_url='store:admin_login')
def admin_dashboard(request):
    if not request.user.is_staff:
        logout(request)
        messages.error(request, 'Access Denied: Staff verification required.')
        return redirect('store:admin_login')

    products = Product.objects.select_related('category').order_by('-created_at')
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    stats = {
        'total': Product.objects.count(),
        'active': Product.objects.filter(status='active').count(),
        'inactive': Product.objects.filter(status='inactive').count(),
        'categories': Category.objects.count(),
    }

    return render(request, 'store/admin/dashboard.html', {
        'page_obj': page_obj,
        'stats': stats,
        'active_admin_nav': 'dashboard',
    })


@login_required(login_url='store:admin_login')
def add_product(request):
    if not request.user.is_staff:
        return redirect('store:admin_login')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, require_image=True)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user
            product.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            messages.success(request, 'Product added to the store.')
            return redirect('store:admin_dashboard')
    else:
        form = ProductForm(require_image=True)

    return render(request, 'store/admin/product_form.html', {
        'form': form,
        'active_admin_nav': 'add',
        'form_title': 'Add a New Product',
        'submit_label': 'Add Product',
        'product': None,
    })


@login_required(login_url='store:admin_login')
def edit_product(request, pk):
    if not request.user.is_staff:
        return redirect('store:admin_login')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, require_image=False)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('store:admin_dashboard')
    else:
        form = ProductForm(instance=product, require_image=False)

    return render(request, 'store/admin/product_form.html', {
        'form': form,
        'active_admin_nav': 'list',
        'form_title': 'Edit Product',
        'submit_label': 'Save Changes',
        'product': product,
    })


@login_required(login_url='store:admin_login')
def delete_product(request, pk):
    if not request.user.is_staff:
        return redirect('store:admin_login')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if product.image:
            product.image.delete(save=False)
        product.delete()
        messages.success(request, 'Product deleted.')
    return redirect('store:admin_dashboard')


@login_required(login_url='store:admin_login')
def admin_settings(request):
    if not request.user.is_staff:
        return redirect('store:admin_login')

    settings_obj = SiteSetting.load()

    if request.method == 'POST':
        form = SiteSettingForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homepage photos and text updated.')
            return redirect('store:admin_settings')
    else:
        form = SiteSettingForm(instance=settings_obj)

    return render(request, 'store/admin/settings.html', {
        'form': form,
        'active_admin_nav': 'settings',
    })


# =====================================================================
# 🚀 ADDED: CUSTOM CORE HOOKS FOR SYSTEM DASHBOARD CONFIGURATIONS
# =====================================================================

@login_required(login_url='store:admin_login')
def manage_bank_account(request):
    """View to support custom storefront dashboard configuration button"""
    if not request.user.is_staff:
        return redirect('store:admin_login')
        
    # Get the existing record if it exists
    bank = BankAccount.objects.first()
    
    if request.method == 'POST':
        account_name = request.POST.get('account_name', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        
        if not account_name or not bank_name or not account_number:
            messages.error(request, 'All fields are required.')
            return render(request, 'store/admin/bank_form.html', {'bank': bank})
        
        try:
            if bank:
                # Update existing record
                bank.account_name = account_name
                bank.bank_name = bank_name
                bank.account_number = account_number
                bank.is_active = True
                bank.save()
            else:
                # 🚀 THE CRITICAL FIX: Capture the newly created object back into the 'bank' variable
                bank = BankAccount.objects.create(
                    account_name=account_name, 
                    bank_name=bank_name, 
                    account_number=account_number, 
                    is_active=True
                )
            
            messages.success(request, 'Bank credentials saved completely.')
            return redirect('store:admin_dashboard')
            
        except Exception as e:
            messages.error(request, f"Database Error: {str(e)}")
            
    return render(request, 'store/admin/bank_form.html', {'bank': bank})


@login_required(login_url='store:admin_login')
def admin_orders(request):
    """Custom view layout to track customer order data without accessing native admin backends"""
    if not request.user.is_staff:
        return redirect('store:admin_login')
        
    orders_qs = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'store/admin/orders_list.html', {'page_obj': page_obj})
