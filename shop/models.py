from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from PIL import Image
import os
import uuid

class Brand(models.Model):
    """برند محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام برند")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="لوگو")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    website = models.URLField(blank=True, verbose_name="وب‌سایت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_products_count(self):
        return self.products.filter(is_active=True).count()

class Category(models.Model):
    """دسته‌بندی محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")
    icon = models.CharField(max_length=50, blank=True, verbose_name="آیکون")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_products_count(self):
        return self.products.filter(is_active=True).count()

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
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
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
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان متا")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات متا")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="کلمات کلیدی متا")
    
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
        # Calculate discount amount if percentage is set
        if self.discount_percentage > 0:
            self.discount_amount = (self.price * self.discount_percentage) / 100
            self.original_price = self.price
            self.price = self.price - self.discount_amount
            self.has_discount = True
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
        """فشرده‌سازی تصویر"""
        if self.image and hasattr(self.image, 'path'):
            try:
                # Check if file exists
                if not os.path.exists(self.image.path):
                    return
                
                img = Image.open(self.image.path)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1200px width/height)
                max_size = (1200, 1200)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save with compression
                img.save(self.image.path, 'JPEG', quality=85, optimize=True)
            except (FileNotFoundError, OSError, Exception) as e:
                # Log error but don't crash
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

@receiver(post_save, sender=ProductImage)
def update_primary_image(sender, instance, created, **kwargs):
    """بروزرسانی تصویر اصلی"""
    if instance.is_primary:
        # Set other images of the same product as non-primary
        ProductImage.objects.filter(
            product=instance.product,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)
