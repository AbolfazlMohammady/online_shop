from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Set product stock quantity for testing'

    def add_arguments(self, parser):
        parser.add_argument('product_name', type=str, help='Product name to update')
        parser.add_argument('stock_quantity', type=int, help='New stock quantity')

    def handle(self, *args, **options):
        product_name = options['product_name']
        stock_quantity = options['stock_quantity']
        
        try:
            # Try exact match first
            try:
                product = Product.objects.get(name=product_name)
            except Product.DoesNotExist:
                # Try partial match
                product = Product.objects.filter(name__contains=product_name).first()
                if not product:
                    raise Product.DoesNotExist
            
            old_stock = product.stock_quantity
            product.stock_quantity = stock_quantity
            product.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Product "{product.name}" stock updated from {old_stock} to {stock_quantity}'
                )
            )
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Product "{product_name}" not found')
            )
