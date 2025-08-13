from django.core.management.base import BaseCommand
from shop.models import Banner
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create a sample banner for testing'

    def handle(self, *args, **options):
        # Check if banner already exists
        if Banner.objects.filter(is_active=True).exists():
            self.stdout.write(
                self.style.WARNING('Active banner already exists. Skipping creation.')
            )
            return

        # Create sample banner
        banner = Banner.objects.create(
            title="تخفیف ویژه تابستانه",
            subtitle="بهترین محصولات آرایشی و بهداشتی با 30٪ تخفیف",
            button_text="همین حالا خرید کنید",
            button_url="/shop/products/",
            discount_percentage=30,
            countdown_hours=72,
            is_active=True,
            banner_type='hero'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created banner: {banner.title}')
        )
