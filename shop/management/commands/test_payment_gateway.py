from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Order, Product, Category
from shop.payment_gateway import payment_gateway
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'تست درگاه پرداخت زرین‌پال'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('شروع تست درگاه پرداخت زرین‌پال...'))
        
        try:
            # ایجاد کاربر تست
            test_user, created = User.objects.get_or_create(
                username='test_user',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'کاربر',
                    'last_name': 'تست',
                    'phone': '09123456789'
                }
            )
            
            if created:
                test_user.set_password('testpass123')
                test_user.save()
                self.stdout.write(self.style.SUCCESS(f'کاربر تست ایجاد شد: {test_user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'کاربر تست موجود است: {test_user.username}'))
            
            # ایجاد دسته‌بندی تست
            test_category, created = Category.objects.get_or_create(
                name='دسته‌بندی تست',
                defaults={'slug': 'test-category'}
            )
            
            # ایجاد محصول تست
            test_product, created = Product.objects.get_or_create(
                name='محصول تست',
                defaults={
                    'slug': 'test-product',
                    'category': test_category,
                    'description': 'این یک محصول تست است',
                    'price': Decimal('100000'),  # 100,000 تومان
                    'stock_quantity': 10
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'محصول تست ایجاد شد: {test_product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'محصول تست موجود است: {test_product.name}'))
            
            # ایجاد سفارش تست
            test_order, created = Order.objects.get_or_create(
                user=test_user,
                status='pending',
                defaults={
                    'subtotal_amount': Decimal('100000'),
                    'shipping_amount': Decimal('50000'),
                    'total_amount': Decimal('150000'),
                    'receiver_name': 'گیرنده تست',
                    'receiver_phone': '09123456789',
                    'province_name': 'تهران',
                    'city_name': 'تهران',
                    'address_detail': 'آدرس تست',
                    'postal_code': '1234567890'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'سفارش تست ایجاد شد: #{test_order.id}'))
            else:
                self.stdout.write(self.style.WARNING(f'سفارش تست موجود است: #{test_order.id}'))
            
            # تست ایجاد درخواست پرداخت
            self.stdout.write('تست ایجاد درخواست پرداخت...')
            
            # آدرس بازگشت فرضی
            callback_url = 'http://127.0.0.1:8000/test-callback/'
            
            payment_result = payment_gateway.create_payment_request(test_order, callback_url)
            
            if payment_result['success']:
                self.stdout.write(self.style.SUCCESS('✅ درخواست پرداخت موفق!'))
                self.stdout.write(f'   Authority: {payment_result["authority"]}')
                self.stdout.write(f'   Payment URL: {payment_result["payment_url"]}')
                self.stdout.write(f'   Message: {payment_result["message"]}')
            else:
                self.stdout.write(self.style.ERROR('❌ درخواست پرداخت ناموفق!'))
                self.stdout.write(f'   Error: {payment_result["message"]}')
                if 'error_code' in payment_result:
                    self.stdout.write(f'   Error Code: {payment_result["error_code"]}')
            
            # تست توضیحات وضعیت
            self.stdout.write('تست توضیحات وضعیت پرداخت...')
            test_statuses = [100, 101, 200, -1, -2, -3]
            for status in test_statuses:
                description = payment_gateway.get_payment_status_description(status)
                self.stdout.write(f'   Status {status}: {description}')
            
            self.stdout.write(self.style.SUCCESS('تست درگاه پرداخت با موفقیت انجام شد!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا در تست درگاه پرداخت: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
