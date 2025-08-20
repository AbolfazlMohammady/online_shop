from django.core.management.base import BaseCommand
from shop.models import Order, Product
from django.db import transaction


class Command(BaseCommand):
    help = 'تنظیم موجودی محصولات بر اساس سفارش‌های پرداخت شده قبلی'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تغییرات بدون اعمال آنها',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 حالت تست - تغییرات اعمال نمی‌شود'))
        
        # پیدا کردن سفارش‌های پرداخت شده
        paid_orders = Order.objects.filter(status='paid')
        
        if not paid_orders.exists():
            self.stdout.write(self.style.SUCCESS('✅ هیچ سفارش پرداخت شده‌ای یافت نشد'))
            return
        
        self.stdout.write(f'📦 یافتن {paid_orders.count()} سفارش پرداخت شده...')
        
        total_items = 0
        inventory_changes = []
        
        for order in paid_orders:
            order_items = order.items.select_related('product').all()
            
            for item in order_items:
                product = item.product
                current_stock = product.stock_quantity
                
                # بررسی اینکه آیا موجودی قبلاً کم شده یا نه
                # اگر موجودی کمتر از تعداد سفارش باشد، احتمالاً قبلاً کم شده
                if current_stock >= item.quantity:
                    # موجودی باید کم شود
                    new_stock = current_stock - item.quantity
                    inventory_changes.append({
                        'product': product.name,
                        'current_stock': current_stock,
                        'order_quantity': item.quantity,
                        'new_stock': new_stock,
                        'order_id': order.id
                    })
                    total_items += 1
        
        if not inventory_changes:
            self.stdout.write(self.style.SUCCESS('✅ تمام موجودی‌ها قبلاً تنظیم شده‌اند'))
            return
        
        self.stdout.write(f'📊 {len(inventory_changes)} محصول نیاز به تنظیم موجودی دارد')
        
        # نمایش تغییرات
        for change in inventory_changes:
            self.stdout.write(
                f'   {change["product"]}: {change["current_stock"]} → {change["new_stock"]} '
                f'(سفارش #{change["order_id"]}: {change["order_quantity"]})'
            )
        
        if not dry_run:
            # اعمال تغییرات
            with transaction.atomic():
                for change in inventory_changes:
                    product = Product.objects.get(name=change['product'])
                    product.stock_quantity = change['new_stock']
                    product.save(update_fields=['stock_quantity'])
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ موجودی {len(inventory_changes)} محصول با موفقیت تنظیم شد')
                )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  برای اعمال تغییرات، دستور را بدون --dry-run اجرا کنید')
            )
