# درگاه پرداخت زرین‌پال - زیبایی شاپ

## معرفی

این پروژه شامل یکپارچه‌سازی کامل درگاه پرداخت زرین‌پال برای فروشگاه آنلاین زیبایی شاپ است. سیستم پرداخت به صورت کامل پیاده‌سازی شده و شامل تمام قابلیت‌های مورد نیاز برای پرداخت الکترونیک است.

## ویژگی‌ها

✅ **پرداخت امن**: استفاده از پروتکل HTTPS و API های امن زرین‌پال  
✅ **پیگیری کامل**: ثبت تمام جزئیات پرداخت و وضعیت‌ها  
✅ **بازگشت خودکار**: بازگشت خودکار کاربر بعد از پرداخت  
✅ **لاگ کامل**: ثبت تمام عملیات در فایل و کنسول  
✅ **مدیریت خطا**: مدیریت کامل خطاها و پیام‌های مناسب  
✅ **پنل مدیریت**: نمایش وضعیت پرداخت در پنل ادمین  

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pipenv install requests
```

### 2. تنظیمات درگاه پرداخت

در فایل `shop/payment_gateway.py` تنظیمات زیر را بررسی کنید:

```python
# تنظیمات درگاه پرداخت
ZARINPAL_MERCHANT_ID = '44a8726a-97be-43b4-ad67-d4e7fe4eae72'
ZARINPAL_SANDBOX = True  # در محیط تولید False کنید
```

### 3. اجرای مایگریشن‌ها

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. تست سیستم

```bash
python manage.py test_payment_gateway
```

## نحوه استفاده

### 1. ایجاد سفارش

```python
from shop.models import Order
from shop.payment_gateway import payment_gateway

# ایجاد سفارش
order = Order.objects.create(
    user=request.user,
    status='pending',
    total_amount=150000,  # 150,000 تومان
    # ... سایر فیلدها
)
```

### 2. شروع پرداخت

```python
# ایجاد درخواست پرداخت
callback_url = request.build_absolute_uri(
    reverse('shop:payment_callback', kwargs={'order_id': order.id})
)

payment_result = payment_gateway.create_payment_request(order, callback_url)

if payment_result['success']:
    # هدایت کاربر به درگاه پرداخت
    return redirect(payment_result['payment_url'])
```

### 3. تایید پرداخت

```python
# در callback
verification_result = payment_gateway.verify_payment(authority, amount)

if verification_result['success']:
    order.mark_as_paid(verification_result['ref_id'], authority)
else:
    order.mark_as_payment_failed(verification_result['error_code'])
```

## ساختار فایل‌ها

```
shop/
├── payment_gateway.py          # کلاس اصلی درگاه پرداخت
├── models.py                   # مدل Order با فیلدهای پرداخت
├── views.py                    # ویوهای پرداخت
├── urls.py                     # URL های پرداخت
├── admin.py                    # پنل ادمین با اطلاعات پرداخت
└── templates/shop/
    ├── order_detail.html       # صفحه جزئیات سفارش
    └── payment_status.html     # صفحه وضعیت پرداخت
```

## فیلدهای جدید در مدل Order

- `payment_authority`: شناسه مرجع پرداخت
- `payment_ref_id`: شماره تراکنش
- `payment_status_code`: کد وضعیت پرداخت
- `payment_description`: توضیحات پرداخت
- `payment_date`: تاریخ پرداخت

## URL های پرداخت

- `initiate_payment`: شروع فرآیند پرداخت
- `payment_callback`: بازگشت از درگاه پرداخت
- `payment_status`: نمایش وضعیت پرداخت

## لاگ‌گیری

تمام عملیات پرداخت در فایل `logs/payment.log` و کنسول ثبت می‌شود:

```
💳 درخواست پرداخت ایجاد شد!
   شماره سفارش: #123
   کاربر: test_user
   مبلغ: 150,000 تومان
   Authority: A123456789012345678901234567890123
   تاریخ: 2025-08-20 10:30:00
==================================================
```

## تست

### تست درگاه پرداخت

```bash
python manage.py test_payment_gateway
```

### تست دستی

1. ایجاد سفارش در سایت
2. کلیک روی دکمه "پرداخت با زرین‌پال"
3. هدایت به درگاه پرداخت
4. بازگشت و تایید پرداخت

## نکات مهم

### محیط تست (Sandbox)
- در محیط توسعه از `ZARINPAL_SANDBOX = True` استفاده کنید
- برای تست از کارت‌های تستی زرین‌پال استفاده کنید

### محیط تولید (Production)
- `ZARINPAL_SANDBOX = False` کنید
- IP سرور را در پنل زرین‌پال ثبت کنید
- از SSL معتبر استفاده کنید

### امنیت
- تمام درخواست‌ها از طریق HTTPS انجام می‌شود
- اعتبارسنجی کامل داده‌ها انجام می‌شود
- لاگ کامل تمام عملیات

## پشتیبانی

در صورت بروز مشکل:

1. بررسی لاگ‌ها در `logs/payment.log`
2. بررسی کنسول برای پیام‌های خطا
3. تست با دستور `test_payment_gateway`
4. بررسی تنظیمات درگاه در پنل زرین‌پال

## منابع

- [مستندات زرین‌پال](https://docs.zarinpal.com/)
- [API Reference](https://docs.zarinpal.com/payment-gateway/)
- [کدهای خطا](https://docs.zarinpal.com/payment-gateway/error-codes/)
