from django.core.management.base import BaseCommand
from shop.models import ProductImage, Brand
import os


class Command(BaseCommand):
    help = 'Clean up ProductImage and Brand records that reference missing image files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Clean up ProductImage records
        self.stdout.write('Checking ProductImage records...')
        missing_product_images = []
        
        for product_image in ProductImage.objects.all():
            if product_image.image and hasattr(product_image.image, 'path'):
                if not os.path.exists(product_image.image.path):
                    missing_product_images.append(product_image)
        
        if missing_product_images:
            self.stdout.write(f'Found {len(missing_product_images)} ProductImage records with missing files:')
            for img in missing_product_images:
                self.stdout.write(f'  - {img.product.name}: {img.image.name}')
            
            if not dry_run:
                count = len(missing_product_images)
                for img in missing_product_images:
                    img.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} ProductImage records with missing files'))
            else:
                self.stdout.write(self.style.WARNING('DRY RUN: Would delete these records'))
        else:
            self.stdout.write(self.style.SUCCESS('No ProductImage records with missing files found'))
        
        # Clean up Brand records
        self.stdout.write('\nChecking Brand records...')
        missing_brand_logos = []
        
        for brand in Brand.objects.all():
            if brand.logo and hasattr(brand.logo, 'path'):
                if not os.path.exists(brand.logo.path):
                    missing_brand_logos.append(brand)
        
        if missing_brand_logos:
            self.stdout.write(f'Found {len(missing_brand_logos)} Brand records with missing logo files:')
            for brand in missing_brand_logos:
                self.stdout.write(f'  - {brand.name}: {brand.logo.name}')
            
            if not dry_run:
                count = len(missing_brand_logos)
                for brand in missing_brand_logos:
                    brand.logo = None  # Clear the logo field instead of deleting the brand
                    brand.save()
                self.stdout.write(self.style.SUCCESS(f'Cleared logo field for {count} Brand records'))
            else:
                self.stdout.write(self.style.WARNING('DRY RUN: Would clear logo fields for these brands'))
        else:
            self.stdout.write(self.style.SUCCESS('No Brand records with missing logo files found'))
        
        self.stdout.write('\nCleanup completed!') 