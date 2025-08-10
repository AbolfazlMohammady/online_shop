from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="نویسنده")
    content = models.TextField(verbose_name="محتوای مقاله")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="خلاصه")
    image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name="تصویر")
    category = models.CharField(max_length=100, default="زیبایی", verbose_name="دسته‌بندی")
    tags = models.CharField(max_length=200, blank=True, verbose_name="برچسب‌ها")
    status = models.CharField(
        max_length=10,
        choices=[
            ('draft', 'پیش‌نویس'),
            ('published', 'منتشر شده'),
        ],
        default='draft',
        verbose_name="وضعیت"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    is_featured = models.BooleanField(default=False, verbose_name="مقاله ویژه")
    
    # Social Media Links
    instagram_link = models.URLField(blank=True, verbose_name="لینک اینستاگرام")
    telegram_link = models.URLField(blank=True, verbose_name="لینک تلگرام")
    
    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_excerpt(self):
        if self.excerpt:
            return self.excerpt
        return self.content[:200] + "..." if len(self.content) > 200 else self.content
    
    def get_tags_list(self):
        """برگرداندن لیست برچسب‌ها"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True, verbose_name="ایمیل")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ اشتراک")
    
    class Meta:
        verbose_name = "اشتراک خبرنامه"
        verbose_name_plural = "اشتراک‌های خبرنامه"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
