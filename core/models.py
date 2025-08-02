from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

def user_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"profile.{ext}"
    return f"users/user_{instance.id}/{filename}"

class Province(models.Model):
    name = models.CharField(verbose_name=_("اسم استان"), unique=True, max_length=511)
    
    def __str__(self) -> str:
        return self.name



class City(models.Model):
    province = models.ForeignKey(Province, verbose_name=_("استان"), on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(verbose_name=_("اسم شهر"), max_length=511)
    
    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='شماره موبایل')
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    profile_image = models.ImageField(
        upload_to=user_profile_image_path, blank=True, null=True, verbose_name='عکس پروفایل'
    )
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='استان')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='شهر')
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name='آدرس دقیق')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.email

    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/img/default-profile.png'  # مسیر عکس پیش‌فرض

    def save(self, *args, **kwargs):
        try:
            this = User.objects.get(id=self.id)
            if this.profile_image and self.profile_image and this.profile_image != self.profile_image:
                if os.path.isfile(this.profile_image.path):
                    os.remove(this.profile_image.path)
        except User.DoesNotExist:
            pass
        super().save(*args, **kwargs)


@receiver(pre_save, sender=User)
def delete_old_profile_image(sender, instance, **kwargs):
    if not instance.pk:
        return  # کاربر جدید است
    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    old_image = old_user.profile_image
    new_image = instance.profile_image
    if old_image and old_image != new_image:
        if old_image.storage.exists(old_image.name):
            old_image.storage.delete(old_image.name)

class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE, verbose_name='کاربر')
    province = models.ForeignKey(Province, on_delete=models.PROTECT, verbose_name='استان')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='شهر')
    detail = models.CharField(max_length=300, verbose_name='آدرس کامل')
    postal_code = models.CharField(max_length=20, verbose_name='کد پستی')
    national_code = models.CharField(max_length=10, verbose_name='کد ملی')
    receiver_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    receiver_phone = models.CharField(max_length=20, verbose_name='شماره تماس گیرنده')
    is_default = models.BooleanField(default=False, verbose_name='آدرس پیش‌فرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
    def __str__(self):
        return f"{self.receiver_name} - {self.city} - {self.detail}"
