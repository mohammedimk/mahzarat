from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image

from .models import Product, SiteSetting, CustomerProfile, Order

ALLOWED_IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp', 'gif')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_uploaded_image(uploaded_file):
    """Shared validation used by both the product photo and site-setting photos"""
    ext = uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError('Photo must be a JPG, PNG, WEBP or GIF file.')
    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError('Photo must be smaller than 5MB.')
    try:
        uploaded_file.seek(0)
        Image.open(uploaded_file).verify()
        uploaded_file.seek(0)
    except Exception:
        raise ValidationError('That file does not appear to be a valid image.')
    return uploaded_file


class AdminRegisterForm(forms.Form):
    full_name = forms.CharField(max_length=100, label='Full name')
    username = forms.CharField(max_length=30, label='Username')
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username.replace('_', '').isalnum():
            raise forms.ValidationError('Username may only contain letters, numbers and underscores.')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('That username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with that email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and len(password) < 6:
            self.add_error('password', 'Password must be at least 6 characters.')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email']
        )
        name_parts = self.cleaned_data['full_name'].strip().split(' ', 1)
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = name_parts[1]
            
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminLoginForm(forms.Form):
    username = forms.CharField(label='Username or email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'old_price', 'description',
            'sizes', 'colors', 'tag', 'status', 'is_featured', 'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Fabric, fit, care instructions…'}),
            'sizes': forms.TextInput(attrs={'placeholder': 'XS,S,M,L,XL'}),
            'colors': forms.TextInput(attrs={'placeholder': '#1F4436,#B08D57,#C98FA1'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'old_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, require_image=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = require_image
        self.fields['image'].widget = forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png,.webp,.gif'})
        self.fields['category'].empty_label = 'Select a category'

    def clean_old_price(self):
        old_price = self.cleaned_data.get('old_price')
        price = self.cleaned_data.get('price')
        if old_price is not None and price is not None and old_price < price:
            raise forms.ValidationError('Original price should normally be higher than the current price.')
        return old_price

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            validate_uploaded_image(image)
        return image


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['hero_title', 'hero_subtitle', 'hero_image', 'lookbook_image_1', 'lookbook_image_2']
        widgets = {
            'hero_subtitle': forms.Textarea(attrs={'rows': 3}),
            'hero_image': forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png,.webp,.gif'}),
            'lookbook_image_1': forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png,.webp,.gif'}),
            'lookbook_image_2': forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png,.webp,.gif'}),
        }

    def _clean_optional_image(self, field_name):
        image = self.cleaned_data.get(field_name)
        if image and hasattr(image, 'size'):
            validate_uploaded_image(image)
        return image

    def clean_hero_image(self):
        return self._clean_optional_image('hero_image')

    def clean_lookbook_image_1(self):
        return self._clean_optional_image('lookbook_image_1')

    def clean_lookbook_image_2(self):
        return self._clean_optional_image('lookbook_image_2')


class CustomerRegisterForm(forms.ModelForm):
    """Customer registration form"""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match!')
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already registered!')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email or username', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))


class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('phone', 'billing_address', 'billing_city', 'billing_state', 'billing_zip')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+234 803 5845 210', 'class': 'form-control'}),
            'billing_address': forms.TextInput(attrs={'placeholder': 'House number/name and street', 'class': 'form-control'}),
            'billing_city': forms.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}),
            'billing_state': forms.TextInput(attrs={'placeholder': 'State/Province', 'class': 'form-control'}),
            'billing_zip': forms.TextInput(attrs={'placeholder': 'Postal/ZIP code', 'class': 'form-control'}),
        }


class CheckoutForm(forms.Form):
    """Checkout form - collects billing details for guests or customers"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name', 'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '+234 803 5845 210', 'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'House/street address', 'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State/Province', 'class': 'form-control'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'ZIP/Postal code', 'class': 'form-control'}))
