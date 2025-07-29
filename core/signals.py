from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User

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