from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Post

# Create your views here.

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published').order_by('-published_at')
        
        # فیلتر بر اساس دسته‌بندی
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # جستجو
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(status='published', is_featured=True)[:3]
        context['categories'] = Post.objects.filter(status='published').values_list('category', flat=True).distinct()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # افزایش تعداد بازدید
        self.object.view_count += 1
        self.object.save()
        
        # مقالات مرتبط
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        
        # مقالات اخیر
        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).exclude(id=self.object.id)[:5]
        
        return context

def blog_home(request):
    """صفحه اصلی بلاگ"""
    featured_posts = Post.objects.filter(status='published', is_featured=True)[:3]
    recent_posts = Post.objects.filter(status='published').order_by('-published_at')[:6]
    categories = Post.objects.filter(status='published').values_list('category', flat=True).distinct()
    
    context = {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    return render(request, 'blog/blog_home.html', context)
