from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'view_count', 'is_featured')
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
        ('آمار', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # اگر مقاله جدید است
            obj.author = request.user
        super().save_model(request, obj, form, change)
