from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product, ProductSpecification, Brand
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create sample product data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create brands first
        brands_data = [
            {
                'name': 'BeautyStyle',
                'description': 'برند معتبر در زمینه لوازم آرایشی و زیبایی',
                'website': 'https://beautystyle.com'
            },
            {
                'name': 'Glamour',
                'description': 'محصولات لوکس و با کیفیت بالا',
                'website': 'https://glamour.com'
            },
            {
                'name': 'Elegance',
                'description': 'طراحی مدرن و شیک برای بانوان',
                'website': 'https://elegance.com'
            },
            {
                'name': 'Chic',
                'description': 'استایل منحصر به فرد و جذاب',
                'website': 'https://chic.com'
            },
            {
                'name': 'Luxe',
                'description': 'محصولات لوکس و گران‌قیمت',
                'website': 'https://luxe.com'
            }
        ]
        
        brands = []
        for brand_data in brands_data:
            # Create a unique slug for Persian text
            base_slug = brand_data['name'].lower().replace(' ', '-')
            slug = base_slug
            counter = 1
            while Brand.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'slug': slug,
                    'description': brand_data['description'],
                    'website': brand_data['website'],
                }
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        # Create categories
        categories_data = [
            {
                'name': 'گیره مو',
                'icon': '🎀',
                'description': 'انواع گیره مو و لوازم آرایش مو'
            },
            {
                'name': 'شال و روسری',
                'icon': '🧣',
                'description': 'شال و روسری های زیبا و شیک'
            },
            {
                'name': 'کیف و کوله',
                'icon': '👜',
                'description': 'کیف و کوله های مدرن و کاربردی'
            },
            {
                'name': 'ساعت و جواهرات',
                'icon': '⌚',
                'description': 'ساعت و جواهرات زیبا و لوکس'
            },
            {
                'name': 'عینک آفتابی',
                'icon': '🕶️',
                'description': 'عینک آفتابی های شیک و محافظ'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            # Create a unique slug for Persian text (FIXED)
            base_slug = cat_data['name'].replace(' ', '-').replace('و', '-')
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slug, # Used the custom generated slug
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Sample products data
        products_data = [
            {
                'name': 'گیره مو کریستالی',
                'category': 'گیره مو',
                'brand': 'BeautyStyle',
                'description': 'گیره مو زیبا با نگین کریستالی، مناسب برای مهمانی‌ها و مراسمات خاص',
                'price': 85000,
                'original_price': 120000,
                'color': 'کریستالی',
                'is_featured': True,
                'is_bestseller': True,
                'rating': 4.5,
                'review_count': 23,
                'stock_quantity': 15
            },
            {
                'name': 'شال ابریشمی گلدار',
                'category': 'شال و روسری',
                'brand': 'Glamour',
                'description': 'شال ابریشمی با طرح گلدار، نرم و لطیف، مناسب فصل بهار و تابستان',
                'price': 180000,
                'original_price': 250000,
                'color': 'صورتی گلدار',
                'is_featured': True,
                'is_new': True,
                'rating': 4.8,
                'review_count': 45,
                'stock_quantity': 8
            },
            {
                'name': 'کیف دستی چرمی',
                'category': 'کیف و کوله',
                'brand': 'Elegance',
                'description': 'کیف دستی چرمی با کیفیت بالا، مناسب کار و مهمانی',
                'price': 450000,
                'original_price': 600000,
                'color': 'مشکی',
                'is_luxury': True,
                'rating': 4.7,
                'review_count': 67,
                'stock_quantity': 5
            },
            {
                'name': 'ساعت مچی زنانه',
                'category': 'ساعت و جواهرات',
                'brand': 'Luxe',
                'description': 'ساعت مچی زیبا با طراحی مدرن، مناسب هدیه',
                'price': 1200000,
                'original_price': 1500000,
                'color': 'طلایی',
                'is_luxury': True,
                'is_featured': True,
                'rating': 4.9,
                'review_count': 89,
                'stock_quantity': 3
            },
            {
                'name': 'عینک آفتابی پولاریزه',
                'category': 'عینک آفتابی',
                'brand': 'Chic',
                'description': 'عینک آفتابی پولاریزه با محافظت کامل از چشم در برابر اشعه UV',
                'price': 320000,
                'original_price': 450000,
                'color': 'مشکی',
                'is_bestseller': True,
                'rating': 4.6,
                'review_count': 34,
                'stock_quantity': 12
            },
            {
                'name': 'گیره مو فلزی',
                'category': 'گیره مو',
                'brand': 'BeautyStyle',
                'description': 'گیره مو فلزی با طراحی ساده و کاربردی',
                'price': 45000,
                'color': 'نقره‌ای',
                'rating': 4.2,
                'review_count': 18,
                'stock_quantity': 25
            },
            {
                'name': 'روسری حریر',
                'category': 'شال و روسری',
                'brand': 'Glamour',
                'description': 'روسری حریر با بافت ظریف و زیبا',
                'price': 95000,
                'original_price': 140000,
                'color': 'آبی',
                'is_new': True,
                'rating': 4.4,
                'review_count': 29,
                'stock_quantity': 10
            },
            {
                'name': 'کوله پشتی چرمی',
                'category': 'کیف و کوله',
                'brand': 'Elegance',
                'description': 'کوله پشتی چرمی با کیفیت بالا و طراحی مدرن',
                'price': 380000,
                'original_price': 520000,
                'color': 'قهوه‌ای',
                'rating': 4.5,
                'review_count': 41,
                'stock_quantity': 7
            },
            {
                'name': 'دستبند نقره',
                'category': 'ساعت و جواهرات',
                'brand': 'Luxe',
                'description': 'دستبند نقره با نگین زیبا، مناسب هدیه',
                'price': 280000,
                'original_price': 380000,
                'color': 'نقره‌ای',
                'is_featured': True,
                'rating': 4.7,
                'review_count': 56,
                'stock_quantity': 9
            },
            {
                'name': 'عینک آفتابی آینه‌ای',
                'category': 'عینک آفتابی',
                'brand': 'Chic',
                'description': 'عینک آفتابی آینه‌ای با طراحی شیک و مدرن',
                'price': 180000,
                'original_price': 250000,
                'color': 'آینه‌ای',
                'is_bestseller': True,
                'rating': 4.3,
                'review_count': 38,
                'stock_quantity': 14
            }
        ]
        
        # Create products
        for product_data in products_data:
            category = next(cat for cat in categories if cat.name == product_data['category'])
            brand = next(brand for brand in brands if brand.name == product_data['brand'])
            
            # Calculate discount percentage
            discount_percentage = 0
            if product_data.get('original_price'):
                discount_percentage = int(((product_data['original_price'] - product_data['price']) / product_data['original_price']) * 100)
            
            # Create a unique slug for Persian text (FIXED)
            base_slug = product_data['name'].replace(' ', '-').replace('و', '-')
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': slug, # Used the custom generated slug
                    'category': category,
                    'brand': brand,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'original_price': product_data.get('original_price'),
                    'discount_percentage': discount_percentage,
                    'color': product_data.get('color', ''),
                    'is_featured': product_data.get('is_featured', False),
                    'is_bestseller': product_data.get('is_bestseller', False),
                    'is_new': product_data.get('is_new', False),
                    'is_luxury': product_data.get('is_luxury', False),
                    'rating': product_data.get('rating', 4.0),
                    'review_count': product_data.get('review_count', 0),
                    'stock_quantity': product_data.get('stock_quantity', 10),
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')
                
                # Add some specifications
                specs_data = [
                    ('جنس', 'کیفیت بالا'),
                    ('ابعاد', 'متوسط'),
                    ('وزن', 'سبک'),
                    ('رنگ', product_data.get('color', 'متنوع')),
                ]
                
                for spec_name, spec_value in specs_data:
                    ProductSpecification.objects.create(
                        product=product,
                        name=spec_name,
                        value=spec_value,
                        order=len(specs_data)
                    )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!')) 