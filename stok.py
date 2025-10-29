import os
import django

# تنظیم DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# بارگذاری تنظیمات Django
django.setup()

# حالا می‌توانید مدل‌ها را وارد کنید
from orders.models import Order, Cart, Profile
from products.models import Product

# کد اصلی اسکریپت
def update_stock():
    """به‌روزرسانی موجودی محصولات بر اساس سفارش‌های تأییدشده"""
    orders = Order.objects.filter(status='confirmed')
    for order in orders:
        for item in order.orderitems.all():
            product = item.product
            product.stock -= item.quantity
            if product.stock < 0:
                print(f"Warning: Negative stock for {product.name}")
            product.save()
        print(f"Updated stock for order {order.uid}")

if __name__ == '__main__':
    print("Starting stock update...")
    update_stock()
    print("Stock update completed.")