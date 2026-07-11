from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image

from .models import Product, SiteSetting

ALLOWED_IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp', 'gif')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_uploaded_image(uploaded_file):
    """Shared validation used by both the product photo and site-setting photos:
    checks extension, file size, and that the file is a genuine image (not just
    something renamed with an image extension)."""
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


# >>> ADD THIS TO store/forms.py AT THE END <<<

class CheckoutForm(forms.Form):
    """Customer details form for checkout"""
    customer_name = forms.CharField(
        max_length=150,
        label='Full name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    customer_email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
    )
    customer_phone = forms.CharField(
        max_length=20,
        label='Phone number',
        widget=forms.TextInput(attrs={'placeholder': '+234 8012345678'})
    )

    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        # Simple phone validation - just check it has digits
        if not any(c.isdigit() for c in phone):
            raise forms.ValidationError('Phone number must contain digits.')
        return phone

