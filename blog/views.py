from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, NewsletterSubscription


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
        
        # فیلتر بر اساس تاریخ
        date_range = self.request.GET.get('date_range')
        if date_range:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            if date_range == 'today':
                queryset = queryset.filter(published_at__date=now.date())
            elif date_range == 'week':
                week_ago = now - timedelta(days=7)
                queryset = queryset.filter(published_at__gte=week_ago)
            elif date_range == 'month':
                month_ago = now - timedelta(days=30)
                queryset = queryset.filter(published_at__gte=month_ago)
            elif date_range == 'year':
                year_ago = now - timedelta(days=365)
                queryset = queryset.filter(published_at__gte=year_ago)
        
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


def newsletter_subscribe(request):
    """اشتراک در خبرنامه"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                subscription, created = NewsletterSubscription.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                if created:
                    messages.success(request, 'اشتراک شما با موفقیت ثبت شد!')
                else:
                    if subscription.is_active:
                        messages.info(request, 'این ایمیل قبلاً در خبرنامه ثبت شده است.')
                    else:
                        subscription.is_active = True
                        subscription.save()
                        messages.success(request, 'اشتراک شما مجدداً فعال شد!')
            except Exception as e:
                messages.error(request, 'خطا در ثبت اشتراک. لطفاً دوباره تلاش کنید.')
        else:
            messages.error(request, 'لطفاً ایمیل خود را وارد کنید.')
    
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'blog:blog_home'))
