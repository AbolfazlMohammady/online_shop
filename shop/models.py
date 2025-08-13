from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from PIL import Image
import os
import uuid
from django.utils.text import slugify

class Brand(models.Model):
    """برند محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام برند")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="لوگو")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    website = models.URLField(blank=True, verbose_name="وب‌سایت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ['name', '-created_at']

    def __str__(self):
        return self.name

    def get_products_count(self):
        return self.products.filter(is_active=True).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class Category(models.Model):
    """دسته‌بندی محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    icon = models.CharField(max_length=50, blank=True, verbose_name="آیکون")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name', '-created_at']

    def __str__(self):
        return self.name

    def get_products_count(self):
        return self.products.filter(is_active=True).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class Product(models.Model):
    """محصول"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('out_of_stock', 'ناموجود'),
    ]

    # Basic Information
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="دسته‌بندی")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="برند")
    description = models.TextField(verbose_name="توضیحات")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="توضیحات کوتاه")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت")
    original_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت اصلی")
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="درصد تخفیف")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="مبلغ تخفیف")
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    min_stock_alert = models.PositiveIntegerField(default=5, verbose_name="حداقل موجودی هشدار")
    
    # Product Details
    model = models.CharField(max_length=100, blank=True, verbose_name="مدل")
    color = models.CharField(max_length=50, blank=True, verbose_name="رنگ")
    size = models.CharField(max_length=50, blank=True, verbose_name="سایز")
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="وزن (گرم)")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="ابعاد")
    
    # Features
    is_featured = models.BooleanField(default=False, verbose_name="محصول ویژه")
    is_bestseller = models.BooleanField(default=False, verbose_name="پرفروش")
    is_new = models.BooleanField(default=False, verbose_name="جدید")
    is_luxury = models.BooleanField(default=False, verbose_name="لوکس")
    has_discount = models.BooleanField(default=False, verbose_name="دارای تخفیف")
    
    # Ratings and Reviews
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="امتیاز")
    review_count = models.PositiveIntegerField(default=0, verbose_name="تعداد نظرات")
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان متا")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات متا")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="کلمات کلیدی متا")
    
    # Social Media
    telegram_link = models.URLField(blank=True, verbose_name="لینک تلگرام")
    instagram_link = models.URLField(blank=True, verbose_name="لینک اینستاگرام")
    facebook_link = models.URLField(blank=True, verbose_name="لینک فیسبوک")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # ساخت اسلاگ خودکار
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        # منطق تخفیف فقط بر اساس original_price
        if self.discount_percentage > 0:
            self.has_discount = True
            if self.original_price:
                self.discount_amount = (self.original_price * self.discount_percentage) / 100
                self.price = self.original_price - self.discount_amount
            else:
                self.original_price = self.price
                self.discount_amount = (self.price * self.discount_percentage) / 100
                self.price = self.price - self.discount_amount
        elif self.discount_amount > 0:
            self.original_price = self.price + self.discount_amount
            self.has_discount = True
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """قیمت نهایی با در نظر گرفتن تخفیف"""
        if self.has_discount:
            return self.price
        return self.price

    @property
    def discount_percentage_calculated(self):
        """محاسبه درصد تخفیف"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """بررسی موجودی"""
        return self.stock_quantity > 0

    @property
    def stock_status(self):
        """وضعیت موجودی"""
        if self.stock_quantity == 0:
            return "ناموجود"
        elif self.stock_quantity <= self.min_stock_alert:
            return "کم موجود"
        return "موجود"

    def update_rating(self):
        """بروزرسانی امتیاز و تعداد نظرات بر اساس کامنت‌های تایید شده"""
        approved_comments = self.comments.filter(is_approved=True)
        if approved_comments.exists():
            total_rating = sum(comment.rating for comment in approved_comments)
            avg_rating = total_rating / approved_comments.count()
            self.rating = round(avg_rating, 1)
            self.review_count = approved_comments.count()
        else:
            self.rating = 0
            self.review_count = 0
        self.save(update_fields=['rating', 'review_count'])

class ProductImage(models.Model):
    """تصاویر محصول"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    image = models.ImageField(upload_to='products/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="متن جایگزین")
    caption = models.CharField(max_length=200, blank=True, verbose_name="عنوان")
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - {self.caption or 'تصویر'}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        
        # Compress image before saving
        if self.image:
            self.compress_image()
        
        super().save(*args, **kwargs)

    def compress_image(self):
        """فشرده‌سازی تصویر با توجه به فرمت"""
        if self.image and hasattr(self.image, 'path'):
            try:
                if not os.path.exists(self.image.path):
                    return
                img = Image.open(self.image.path)
                ext = os.path.splitext(self.image.path)[1].lower()
                max_size = (1200, 1200)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                if img.mode != 'RGB' and ext in ['.jpg', '.jpeg']:
                    img = img.convert('RGB')
                # اگر PNG باشد، بهینه‌سازی مخصوص PNG
                if ext == '.png':
                    img.save(self.image.path, 'PNG', optimize=True)
                else:
                    # اگر پسوند PNG است اما می‌خواهیم JPEG ذخیره کنیم، پسوند را هم تغییر بده
                    if ext == '.png':
                        new_path = self.image.path[:-4] + '.jpg'
                        img = img.convert('RGB')
                        img.save(new_path, 'JPEG', quality=85, optimize=True)
                        os.remove(self.image.path)
                        self.image.name = self.image.name[:-4] + '.jpg'
                    else:
                        img.save(self.image.path, 'JPEG', quality=85, optimize=True)
            except (FileNotFoundError, OSError, Exception) as e:
                print(f"Error compressing image {self.image.path}: {e}")
                pass

class ProductSpecification(models.Model):
    """مشخصات محصول"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications', verbose_name="محصول")
    name = models.CharField(max_length=100, verbose_name="نام مشخصه")
    value = models.CharField(max_length=500, verbose_name="مقدار")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات محصولات"
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

class Comment(models.Model):
    """نظرات محصولات"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name="کاربر")
    name = models.CharField(max_length=100, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="امتیاز")
    comment = models.TextField(verbose_name="نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating when comment is saved
        self.product.update_rating()


# Cart, Wishlist, and Order models
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', verbose_name="کاربر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"سبد {self.user} ({'فعال' if self.is_active else 'غیرفعال'})"

    def get_total_amount(self):
        total = 0
        for item in self.items.select_related('product'):
            total += int(item.price) * item.quantity
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="سبد")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items', verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="تعداد")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت در زمان افزودن")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سبد"
        verbose_name_plural = "آیتم‌های سبد"
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist', verbose_name="کاربر")
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True, verbose_name="محصولات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"

    def __str__(self):
        return f"علاقه‌مندی‌های {self.user}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شد'),
        ('delivered', 'تحویل شد'),
        ('canceled', 'لغو شده'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="جمع جزء")
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="هزینه ارسال")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مبلغ کل")

    # Shipping info snapshot
    receiver_name = models.CharField(max_length=100, verbose_name="نام گیرنده")
    receiver_phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    province_name = models.CharField(max_length=100, verbose_name="استان")
    city_name = models.CharField(max_length=100, verbose_name="شهر")
    address_detail = models.CharField(max_length=300, verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="تعداد")
    unit_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت واحد")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت کل")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

class Settings(models.Model):
    """تنظیمات کلی فروشگاه"""
    key = models.CharField(max_length=100, unique=True, verbose_name="کلید")
    value = models.TextField(verbose_name="مقدار")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "تنظیمات"
        verbose_name_plural = "تنظیمات"
        ordering = ['key']

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get_value(cls, key, default=None):
        """دریافت مقدار تنظیمات"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value, description=""):
        """تنظیم مقدار"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': str(value), 'description': description}
        )
        if not created:
            setting.value = str(value)
            setting.description = description
            setting.save()
        return setting

class ShippingSettings(models.Model):
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=0, default=70000)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=0, default=500000)
    
    class Meta:
        verbose_name = "تنظیمات ارسال"
        verbose_name_plural = "تنظیمات ارسال"
    
    def __str__(self):
        return f"تنظیمات ارسال - هزینه: {self.shipping_cost} تومان"


class Banner(models.Model):
    BANNER_TYPES = [
        ('hero', 'بنر اصلی'),
        ('promo', 'بنر تبلیغاتی'),
        ('category', 'بنر دسته‌بندی'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="عنوان بنر")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="زیرعنوان")
    image = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="تصویر بنر")
    button_text = models.CharField(max_length=50, default="همین حالا خرید کنید", verbose_name="متن دکمه")
    button_url = models.CharField(max_length=200, default="#", verbose_name="لینک دکمه")
    discount_percentage = models.IntegerField(default=30, verbose_name="درصد تخفیف")
    countdown_hours = models.IntegerField(default=48, verbose_name="ساعت باقی‌مانده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='hero', verbose_name="نوع بنر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_banner_type_display()}"
    
    @property
    def countdown_end_time(self):
        """محاسبه زمان پایان شمارش معکوس"""
        from django.utils import timezone
        if self.updated_at:
            return self.updated_at + timezone.timedelta(hours=self.countdown_hours)
        return None
    
    @property
    def is_expired(self):
        """بررسی انقضای بنر"""
        from django.utils import timezone
        if self.countdown_end_time:
            return timezone.now() > self.countdown_end_time
        return False

# Signals for deleting old images
@receiver(pre_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    """حذف فایل تصویر از سرور هنگام حذف رکورد"""
    if instance.image and hasattr(instance.image, 'path'):
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (FileNotFoundError, OSError, Exception) as e:
            print(f"Error deleting image file {instance.image.path}: {e}")
            pass

@receiver(pre_delete, sender=Brand)
def delete_brand_logo_file(sender, instance, **kwargs):
    """حذف فایل لوگو از سرور هنگام حذف برند"""
    if instance.logo and hasattr(instance.logo, 'path'):
        try:
            if os.path.isfile(instance.logo.path):
                os.remove(instance.logo.path)
        except (FileNotFoundError, OSError, Exception) as e:
            print(f"Error deleting logo file {instance.logo.path}: {e}")
            pass

@receiver(pre_delete, sender=Banner)
def delete_banner_image_file(sender, instance, **kwargs):
    """حذف فایل تصویر بنر از سرور هنگام حذف بنر"""
    if instance.image and hasattr(instance.image, 'path'):
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (FileNotFoundError, OSError, Exception) as e:
            print(f"Error deleting banner image file {instance.image.path}: {e}")
            pass

@receiver(post_save, sender=ProductImage)
def update_primary_image(sender, instance, created, **kwargs):
    """بروزرسانی تصویر اصلی"""
    if instance.is_primary:
        # اگر همین تصویر تنها primary است، کاری نکن
        others = ProductImage.objects.filter(product=instance.product, is_primary=True).exclude(id=instance.id)
        if others.exists():
            others.update(is_primary=False)
