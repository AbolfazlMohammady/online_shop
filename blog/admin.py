from django.contrib import admin
from .models import Post, NewsletterSubscription

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'is_featured')
    list_filter = ('status', 'category', 'is_featured', 'published_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('تصویر و دسته‌بندی', {
            'fields': ('image', 'category', 'tags')
        }),
        ('تنظیمات انتشار', {
            'fields': ('status', 'published_at', 'is_featured')
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('instagram_link', 'telegram_link'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # اگر مقاله جدید است
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    ordering = ('-subscribed_at',)
