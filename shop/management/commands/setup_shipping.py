from django.core.management.base import BaseCommand
from shop.models import ShippingSettings, Settings

class Command(BaseCommand):
    help = 'تنظیم هزینه ارسال و آستانه ارسال رایگان'

    def add_arguments(self, parser):
        parser.add_argument(
            '--shipping-cost',
            type=int,
            default=0,
            help='هزینه ارسال به تومان (پیش‌فرض: 0)'
        )
        parser.add_argument(
            '--free-threshold',
            type=int,
            default=500000,
            help='آستانه ارسال رایگان به تومان (پیش‌فرض: 500000)'
        )

    def handle(self, *args, **options):
        shipping_cost = options['shipping_cost']
        free_threshold = options['free_threshold']
        
        self.stdout.write(f'تنظیم هزینه ارسال: {shipping_cost:,} تومان')
        self.stdout.write(f'آستانه ارسال رایگان: {free_threshold:,} تومان')
        
        # تنظیم ShippingSettings
        shipping_setting, created = ShippingSettings.objects.get_or_create(
            id=1,
            defaults={
                'shipping_cost': shipping_cost,
                'free_shipping_threshold': free_threshold
            }
        )
        
        if not created:
            shipping_setting.shipping_cost = shipping_cost
            shipping_setting.free_shipping_threshold = free_threshold
            shipping_setting.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ تنظیمات هزینه ارسال با موفقیت ذخیره شد!'
            )
        )
        
        # نمایش تنظیمات فعلی
        self.stdout.write('\nتنظیمات فعلی:')
        self.stdout.write(f'  هزینه ارسال: {shipping_setting.shipping_cost:,} تومان')
        self.stdout.write(f'  آستانه ارسال رایگان: {shipping_setting.free_shipping_threshold:,} تومان')
        
        # همچنین در Settings هم ذخیره کن
        Settings.set_value('shipping_cost', str(shipping_cost), 'هزینه ارسال به تومان')
        Settings.set_value('free_shipping_threshold', str(free_threshold), 'آستانه ارسال رایگان به تومان')
        
        self.stdout.write(
            self.style.SUCCESS(
                '✅ تنظیمات در مدل Settings نیز ذخیره شد!'
            )
        )
