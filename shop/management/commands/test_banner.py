from django.core.management.base import BaseCommand
from shop.models import Banner
from django.utils import timezone


class Command(BaseCommand):
    help = 'Test banner functionality'

    def handle(self, *args, **options):
        # Get the first active banner
        banner = Banner.objects.filter(is_active=True).first()
        
        if not banner:
            self.stdout.write(
                self.style.WARNING('No active banner found.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Banner Title: {banner.title}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Banner Subtitle: {banner.subtitle}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Discount Percentage: {banner.discount_percentage}%')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Countdown Hours: {banner.countdown_hours}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created At: {banner.created_at}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Updated At: {banner.updated_at}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Countdown End Time: {banner.countdown_end_time}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Is Expired: {banner.is_expired}')
        )
        
        # Calculate remaining time
        if banner.countdown_end_time:
            now = timezone.now()
            remaining = banner.countdown_end_time - now
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                self.stdout.write(
                    self.style.SUCCESS(f'Remaining Time: {hours} hours, {minutes} minutes')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Banner has expired!')
                )
