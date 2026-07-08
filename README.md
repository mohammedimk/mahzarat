# Botokhan Store — Django (Python) E-Commerce Website

The same women's clothing store — public storefront (homepage, categories,
product pages, search, cart) plus an admin panel where an admin can
**register, log in, and upload/manage the clothing photos and product
details** — rebuilt on **Django** instead of PHP.

## Requirements
- Python 3.10+
- pip

## 1. Set up a virtual environment and install dependencies
```bash
cd botokhan_django
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` installs Django and Pillow (needed for image handling).

## 2. Configure the database
By default the project uses **SQLite** — zero setup, a single `db.sqlite3`
file, perfect for development or a small store. Nothing to configure; skip to
step 3.

**To use MySQL instead:**
```bash
pip install mysqlclient
```
Then open `botokhan/settings.py` and replace the `DATABASES` block with the
commented-out MySQL example already in that file (just fill in your DB name,
user and password), and create the MySQL database first:
```sql
CREATE DATABASE botokhan_store CHARACTER SET utf8mb4;
```

PostgreSQL works the same way with `django.db.backends.postgresql` and
`psycopg2-binary`.

## 3. Create the database tables
```bash
python manage.py migrate
```
This creates all tables and seeds 5 starter categories (Dresses, Ankara &
Prints, Co-ord Sets, Outerwear, Accessories) automatically via a data
migration — nothing else to run.

## 4. Run the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/`.

## 5. Create your admin account and start adding products
1. Go to `http://127.0.0.1:8000/admin-panel/register/` and create your admin
   account (full name, username, email, password).
2. Log in at `/admin-panel/login/` — you land on the dashboard.
3. **Add Product** → name, category, price, description, sizes, colors, an
   optional New/Sale/Trending/Best seller badge, and the **photo upload** —
   this photo is exactly what shoppers see on the store.
4. Toggle Active/Inactive to show or hide a product without deleting it, and
   check "Feature in Editor's Picks" to spotlight it on the homepage.
5. **Homepage Photos** in the sidebar lets you replace the hero banner photo,
   the two lookbook photos, and edit the hero headline/subtitle.

Everything an admin uploads appears immediately on the public store.

> Django's own built-in admin site is also available at `/django-admin/` if
> you ever want deeper, spreadsheet-style management — but you'll need to
> create a superuser for it separately with `python manage.py createsuperuser`.
> The `/admin-panel/` interface described above is the polished, purpose-built
> one made for day-to-day product management.

## Project structure
```
botokhan_django/
├── manage.py
├── requirements.txt
├── botokhan/                     Project settings package
│   ├── settings.py                Edit database/config here
│   ├── urls.py
│   └── ...
├── store/                        The app — everything lives here
│   ├── models.py                  Category, Product, SiteSetting
│   ├── forms.py                   Registration/login/product/settings forms + image validation
│   ├── views.py                   All public + admin views
│   ├── urls.py                    /admin-panel/... routes live here
│   ├── admin.py                   Optional Django-admin registration
│   ├── context_processors.py      Makes categories/currency available everywhere
│   ├── templatetags/store_extras.py   {{ price|currency }} filter, dict lookups
│   ├── migrations/0001_initial.py Creates tables + seeds categories
│   ├── static/store/css/          style.css (storefront) / admin.css (admin)
│   └── templates/store/           All HTML templates
│       ├── base.html               Storefront layout, cart drawer, quick view, JS
│       ├── index.html / category.html / product.html / search.html
│       └── admin/                  register, login, dashboard, product_form, settings
└── media/                        Every uploaded photo lives here (product + site photos)
```

## How the storefront works
- **Cart**: a lightweight client-side cart (drawer + quick view) built with
  vanilla JS. No payment processor is wired up — the "Checkout" button is a
  placeholder, ready to connect to Paystack/Flutterwave/Stripe later.
- **Category tiles** on the homepage automatically show the most recently
  added photo in that category.
- **Views** on each product increase every time its page is opened.
- Product data needed by the cart/quick-view JS is safely embedded per-page
  using Django's `json_script` filter (no extra API calls needed).

## Security notes (already built in)
- Passwords are hashed by Django's authentication system (PBKDF2 by default)
  — never stored in plain text.
- All database access goes through the **Django ORM** — parameterized
  queries throughout, protected against SQL injection.
- **CSRF protection** is on by default for every POST form (Django's
  `{% csrf_token %}`), including the delete-product action.
- Uploaded photos are validated: extension whitelist, 5MB size limit, and a
  genuine-image check via Pillow (`Image.verify()`) — not just a matching
  file extension.
- All template output is auto-escaped by Django to prevent stored XSS.
- `ALLOWED_HOSTS` and `DEBUG` are called out clearly in `settings.py` for you
  to lock down before deploying.

## Locking down registration (recommended before going live)
Right now anyone who finds `/admin-panel/register/` can create an admin
account. Once your admin accounts exist, either:
- Remove the `admin_register` URL/view, or
- Add an invite-code check to `AdminRegisterForm`, or
- Ask to have it converted into an invite-only flow where only an existing
  admin can create new admin accounts from inside the dashboard.

## Customizing
- **Colors / fonts**: edit the CSS variables at the top of
  `store/static/store/css/style.css` (storefront) and `admin.css` (admin).
- **Categories**: add/remove rows via `/django-admin/` (after creating a
  superuser) or directly in the database — they show up automatically in the
  nav, filters, and product form.
- **Currency**: `STORE_CURRENCY_SYMBOL` in `settings.py`, used by the
  `{{ value|currency }}` template filter in `store/templatetags/store_extras.py`.

## Deploying
For production: set `DEBUG = False`, set a real `SECRET_KEY` and
`ALLOWED_HOSTS` in `settings.py`, run `python manage.py collectstatic`, and
serve `static/` and `media/` via your web server (Nginx/Apache) or a service
like WhiteNoise/S3 — Django does not serve them efficiently on its own in
production.

## Want more features?
This can be extended with: real checkout/payment (Paystack/Flutterwave),
order management, multiple photos per product, customer accounts, coupon
codes, or moving photo storage to a cloud bucket (S3/Cloudinary) instead of
the local `media/` folder. Just ask.
