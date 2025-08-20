from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import datetime, timedelta
import jdatetime

register = template.Library()

@register.filter
def add_commas(value):
    """اضافه کردن کاما به اعداد"""
    try:
        # تبدیل به عدد
        num = float(value)
        # تبدیل به رشته با کاما
        return f"{num:,.0f}"
    except (ValueError, TypeError):
        return value

@register.filter
def persian_date(value):
    """تبدیل تاریخ میلادی به شمسی"""
    if not value:
        return ""
    
    try:
        # تبدیل به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime("%Y/%m/%d")
    except:
        return value.strftime("%Y/%m/%d") if hasattr(value, 'strftime') else str(value)

@register.filter
def persian_datetime(value):
    """تبدیل تاریخ و زمان میلادی به شمسی"""
    if not value:
        return ""
    
    try:
        # تبدیل به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime("%Y/%m/%d %H:%M")
    except:
        return value.strftime("%Y/%m/%d %H:%M") if hasattr(value, 'strftime') else str(value)

@register.filter
def jalali_date(value):
    """تبدیل تاریخ میلادی به شمسی (فقط تاریخ)"""
    if not value:
        return ""
    
    try:
        # تبدیل به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime("%Y/%m/%d")
    except:
        return value.strftime("%Y/%m/%d") if hasattr(value, 'strftime') else str(value)

@register.filter
def jalali_datetime(value):
    """تبدیل تاریخ و زمان میلادی به شمسی"""
    if not value:
        return ""
    
    try:
        # تبدیل به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime("%Y/%m/%d %H:%M")
    except:
        return value.strftime("%Y/%m/%d %H:%M") if hasattr(value, 'strftime') else str(value)

@register.filter
def time_ago(value):
    """نمایش زمان گذشته (مثل 2 ساعت پیش)"""
    if not value:
        return ""
    
    # استفاده از timezone-aware datetime
    now = timezone.now()
    
    # اگر value timezone-naive است، آن را timezone-aware کنیم
    if isinstance(value, datetime) and timezone.is_naive(value):
        value = timezone.make_aware(value)
    elif isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
        except:
            return str(value)
    
    diff = now - value
    
    if diff.days > 0:
        return f"{diff.days} روز پیش"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ساعت پیش"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} دقیقه پیش"
    else:
        return "لحظاتی پیش"

@register.filter
def timesince_fa(value):
    """نمایش زمان گذشته به فارسی (مثل 2 ساعت پیش)"""
    if not value:
        return ""
    
    # استفاده از timezone-aware datetime
    now = timezone.now()
    
    # اگر value timezone-naive است، آن را timezone-aware کنیم
    if isinstance(value, datetime) and timezone.is_naive(value):
        value = timezone.make_aware(value)
    elif isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
        except:
            return str(value)
    
    diff = now - value
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} سال پیش"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} ماه پیش"
    elif diff.days > 7:
        weeks = diff.days // 7
        return f"{weeks} هفته پیش"
    elif diff.days > 0:
        return f"{diff.days} روز پیش"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ساعت پیش"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} دقیقه پیش"
    else:
        return "لحظاتی پیش"