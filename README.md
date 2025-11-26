# 🛒 Django E-commerce Platform

A comprehensive, production-ready e-commerce web application built with Django, featuring complete shopping functionality, user management, order processing, and a modular architecture designed for scalability and easy customization.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

## 🌟 Overview

This Django-based e-commerce platform provides a solid foundation for building online stores, complete with essential features like product catalog management, shopping cart functionality, order processing, and user authentication. The modular architecture makes it easy to extend with additional features like payment gateways, REST APIs, or advanced inventory management.

**Perfect for:**
- Learning Django and e-commerce development
- Building MVPs for online stores
- Academic projects and portfolio pieces
- Base template for commercial applications

## ✨ Key Features

### 🔐 User Management
- User registration with email verification
- Secure login/logout functionality
- Password reset and recovery
- User profile management
- Order history tracking
- Address management

### 🛍️ Product Management
- Comprehensive product catalog
- Hierarchical category system
- Multiple product images per item
- Product variants and attributes
- Stock tracking
- Featured products
- Product search and filtering

### 🛒 Shopping Experience
- Dynamic shopping cart
- Real-time cart updates
- Session-based cart for guests
- Persistent cart for registered users
- Cart quantity management
- Price calculations with tax

### 📦 Order Processing
- Seamless checkout process
- Order creation and tracking
- Order status management
- Order history for users
- Admin order management
- Invoice generation

### 📄 Content Pages
- Dynamic About Us page
- Contact form with email integration
- Terms & Conditions
- Privacy Policy
- FAQ section
- Blog/News (optional)

### ⚙️ Technical Features
- Responsive design (mobile-first)
- RESTful URL structure
- Environment-based configuration
- Secure SECRET_KEY management
- Static and media file handling
- Database migrations support
- Admin dashboard customization
- CSRF protection
- SQL injection prevention

## 🛠️ Technology Stack

- **Backend Framework**: Django 4.2+
- **Language**: Python 3.10+
- **Database**: SQLite (default), PostgreSQL, MySQL compatible
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Django Templates
- **Form Handling**: Django Forms
- **Authentication**: Django Auth System
- **Admin Interface**: Django Admin (customized)
- **Static Files**: Django Static Files Handler

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (usually comes with Python)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **virtualenv** (recommended) - `pip install virtualenv`
- **Database** (optional): PostgreSQL or MySQL for production

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/mehdiseyfie/django_ecommerce_project.git
cd django_ecommerce_project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the `config/` directory:

```bash
cp config/.env.example config/.env
```

Edit the `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-a-strong-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# SQLite (default)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (production recommended)
# DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db

# MySQL
# DATABASE_URL=mysql://user:password@localhost:3306/ecommerce_db

# Email Configuration (for password reset, order notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static & Media Files
STATIC_URL=/static/
MEDIA_URL=/media/

# Security Settings (Production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### Step 5: Generate SECRET_KEY

Generate a strong SECRET_KEY for Django:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it into your `.env` file.

### Step 6: Database Migration

```bash
# Create database tables
python manage.py migrate

# Create initial data (optional)
python manage.py loaddata initial_data.json  # if available
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 8: Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### Step 9: Run Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** to see your application.

Access the admin panel at **http://127.0.0.1:8000/admin/**

## 📂 Project Structure

```
django_ecommerce_project/
│
├── accounts/                    # User authentication & authorization
│   ├── migrations/
│   ├── templates/
│   ├── models.py               # User profile models
│   ├── views.py                # Login, register, profile views
│   ├── forms.py                # User forms
│   └── urls.py
│
├── products/                    # Product catalog management
│   ├── migrations/
│   ├── templates/
│   ├── models.py               # Product, Category models
│   ├── views.py                # Product listing, detail views
│   ├── admin.py                # Admin customization
│   └── urls.py
│
├── products_images/             # Product image management
│   ├── models.py               # ProductImage model
│   └── admin.py
│
├── cart/                        # Shopping cart functionality
│   ├── cart.py                 # Cart session management
│   ├── views.py                # Add, remove, update cart
│   ├── forms.py                # Cart forms
│   └── urls.py
│
├── orders/                      # Order processing & management
│   ├── migrations/
│   ├── templates/
│   ├── models.py               # Order, OrderItem models
│   ├── views.py                # Checkout, order views
│   ├── admin.py
│   └── urls.py
│
├── customers/                   # Customer profiles & history
│   ├── models.py               # Customer profile
│   ├── views.py                # Profile, order history
│   └── urls.py
│
├── pages/                       # Static content pages
│   ├── templates/
│   ├── views.py                # About, Contact views
│   ├── forms.py                # Contact form
│   └── urls.py
│
├── config/                      # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   ├── asgi.py                 # ASGI configuration
│   ├── .env.example            # Environment template
│   └── .env                    # Environment variables (gitignored)
│
├── static/                      # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── vendor/
│
├── media/                       # User-uploaded files
│   ├── products/
│   └── profiles/
│
├── templates/                   # Global templates
│   ├── base.html               # Base template
│   ├── navbar.html             # Navigation
│   ├── footer.html             # Footer
│   └── home.html               # Homepage
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## 🎯 Usage Guide

### For Customers

1. **Browse Products**: Visit the homepage and explore product categories
2. **Search**: Use the search bar to find specific products
3. **Add to Cart**: Click "Add to Cart" on product pages
4. **View Cart**: Click the cart icon to review your items
5. **Checkout**: Proceed to checkout and complete your order
6. **Track Orders**: View order history in your profile

### For Administrators

1. **Access Admin Panel**: Go to `/admin/` and log in
2. **Manage Products**: Add, edit, or delete products and categories
3. **Process Orders**: View and update order statuses
4. **Manage Users**: View and manage customer accounts
5. **Content Management**: Update static pages and site content

### Common Management Commands

```bash
# Create a new app
python manage.py startapp app_name

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Shell access
python manage.py shell

# Database shell
python manage.py dbshell

# Check for issues
python manage.py check
```

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 🚢 Deployment

### Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Set up proper email backend
- [ ] Configure static and media file serving
- [ ] Enable HTTPS and security settings
- [ ] Set up regular database backups
- [ ] Configure logging
- [ ] Set up monitoring and error tracking

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-production-secret-key

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

### Deploy to Popular Platforms

#### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn config.wsgi" > Procfile

# Create runtime.txt
echo "python-3.10.12" > runtime.txt

# Deploy
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### AWS / DigitalOcean / VPS

Use gunicorn + nginx for production serving. Example with gunicorn:

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔒 Security Best Practices

- Never commit `.env` file or `SECRET_KEY`
- Always use HTTPS in production
- Keep Django and dependencies updated
- Use environment variables for sensitive data
- Enable Django security middleware
- Implement rate limiting for forms
- Sanitize user inputs
- Regular security audits
- Use CSP (Content Security Policy)
- Implement proper error handling

## 🎨 Customization

### Adding New Features

1. **Create a new Django app**:
   ```bash
   python manage.py startapp feature_name
   ```

2. **Add to INSTALLED_APPS** in `config/settings.py`

3. **Create models, views, and templates**

4. **Register URLs** in app's `urls.py` and include in main `urls.py`

### Styling

- Modify CSS files in `static/css/`
- Update templates in `templates/` directory
- Use Django template inheritance for consistency

### Adding Payment Gateway

Integrate popular payment processors:
- **Stripe**: Follow [Stripe Django docs](https://stripe.com/docs/payments)
- **PayPal**: Use [django-paypal](https://github.com/spookylukey/django-paypal)
- **Razorpay**: Check [Razorpay Python SDK](https://razorpay.com/docs/payment-gateway/server-integration/python/)

## 🔮 Roadmap & Future Enhancements

- [ ] Payment gateway integration (Stripe, PayPal)
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Advanced search with filters
- [ ] Discount codes and coupons
- [ ] Inventory management
- [ ] Multi-vendor support
- [ ] REST API with Django REST Framework
- [ ] Mobile app integration
- [ ] Email notifications for orders
- [ ] Social media authentication
- [ ] Product recommendations (AI/ML)
- [ ] Analytics dashboard
- [ ] Multi-language support (i18n)
- [ ] Multi-currency support

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Contribute

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow [PEP 8](https://pep8.org/) style guide
- Write meaningful commit messages
- Add docstrings to functions and classes
- Include tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Bootstrap](https://getbootstrap.com/) - Frontend framework
- All contributors who help improve this project

## 📧 Contact & Support

**Mehdi Seyfie**

- GitHub: [@mehdiseyfie](https://github.com/mehdiseyfie)
- Email: [mmmehdiseyfi@gmail.com](mailto:mmmehdiseyfi@gmail.com)

### Get Help

- 📖 Check the [Wiki](https://github.com/mehdiseyfie/django_ecommerce_project/wiki) (if available)
- 🐛 Report bugs via [Issues](https://github.com/mehdiseyfie/django_ecommerce_project/issues)
- 💬 Ask questions in [Discussions](https://github.com/mehdiseyfie/django_ecommerce_project/discussions)

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub! It helps others discover the project and motivates continued development.

---

<div align="center">

**Made with ❤️ by Mehdi Seyfie**

[⬆ Back to Top](#-django-e-commerce-platform)

</div>
