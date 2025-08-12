from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_commas(value):
    """اضافه کردن کاما به اعداد برای نمایش بهتر قیمت‌ها"""
    if value is None:
        return '0'
    try:
        # تبدیل به عدد و سپس به رشته با کاما
        num = int(float(value))
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(value)

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


# ------- Persian/Jalali helpers -------
PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

def _to_persian_digits(text: str) -> str:
    return ''.join(PERSIAN_DIGITS.get(ch, ch) for ch in str(text))

def _gregorian_to_jalali(gy: int, gm: int, gd: int):
    """Convert Gregorian to Jalali (algorithmic, no external deps). Returns (jy, jm, jd)."""
    g_d_m = [0,31,59,90,120,151,181,212,243,273,304,334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gm > 2 and (gy + 1) or gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

@register.filter(name='to_persian_digits')
def to_persian_digits(value):
    """Convert Latin digits to Persian digits."""
    return _to_persian_digits(value)

def _format_jalali(dt: datetime, include_time: bool = True) -> str:
    if not dt:
        return ''
    # Ensure aware -> convert to local timezone if needed
    if timezone.is_aware(dt):
        dt_local = timezone.localtime(dt)
    else:
        dt_local = dt
    jy, jm, jd = _gregorian_to_jalali(dt_local.year, dt_local.month, dt_local.day)
    hh = f"{dt_local.hour:02d}"
    mm = f"{dt_local.minute:02d}"
    date_part = f"{jy:04d}/{jm:02d}/{jd:02d}"
    if include_time:
        result = f"{date_part} {hh}:{mm}"
    else:
        result = date_part
    return _to_persian_digits(result)

@register.filter(name='jalali_date')
def jalali_date(value):
    """Format datetime/date to Jalali date (YYYY/MM/DD) with Persian digits."""
    if not value:
        return ''
    if isinstance(value, datetime):
        return _format_jalali(value, include_time=False)
    # date instance
    dt = datetime(year=value.year, month=value.month, day=value.day)
    return _format_jalali(dt, include_time=False)

@register.filter(name='jalali_datetime')
def jalali_datetime(value):
    """Format datetime to Jalali date and time with Persian digits."""
    if not value:
        return ''
    return _format_jalali(value, include_time=True)