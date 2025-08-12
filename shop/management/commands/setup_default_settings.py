from django.core.management.base import BaseCommand
from shop.models import Settings

class Command(BaseCommand):
    help = 'تنظیم مقادیر پیش‌فرض برای فروشگاه'

    def handle(self, *args, **options):
        # تنظیم هزینه ارسال پیش‌فرض
        Settings.set_value(
            'shipping_cost',
            '70000',
            'هزینه ارسال پیش‌فرض (تومان)'
        )
        
        # تنظیم حد آستانه ارسال رایگان
        Settings.set_value(
            'free_shipping_threshold',
            '500000',
            'حد آستانه برای ارسال رایگان (تومان)'
        )
        
        # تنظیم نام فروشگاه
        Settings.set_value(
            'shop_name',
            'زیبایی شاپ',
            'نام فروشگاه'
        )
        
        # تنظیم توضیحات فروشگاه
        Settings.set_value(
            'shop_description',
            'فروشگاه آرایشی و بهداشتی',
            'توضیحات فروشگاه'
        )
        
        self.stdout.write(
            self.style.SUCCESS('تنظیمات پیش‌فرض با موفقیت ایجاد شد!')
        )

