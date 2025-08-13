from django.core.management.base import BaseCommand
from shop.models import Banner
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update existing banner to fix countdown timer'

    def handle(self, *args, **options):
        # Get the first active banner
        banner = Banner.objects.filter(is_active=True).first()
        
        if not banner:
            self.stdout.write(
                self.style.WARNING('No active banner found.')
            )
            return
        
        # Update the banner to trigger updated_at change
        banner.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated banner: {banner.title}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Countdown hours: {banner.countdown_hours}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'End time: {banner.countdown_end_time}')
        )
