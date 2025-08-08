from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def timesince_fa(value):
    """نمایش زمان به صورت فارسی"""
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    # تبدیل به ثانیه
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'چند ثانیه پیش'
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f'{minutes} دقیقه پیش'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours} ساعت پیش'
    elif seconds < 2592000:  # 30 روز
        days = int(seconds // 86400)
        return f'{days} روز پیش'
    elif seconds < 31536000:  # 365 روز
        months = int(seconds // 2592000)
        return f'{months} ماه پیش'
    else:
        years = int(seconds // 31536000)
        return f'{years} سال پیش' 