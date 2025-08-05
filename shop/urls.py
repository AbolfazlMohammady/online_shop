from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Product listing and filtering
    path('products/', views.product_list, name='product_list'),
    path('products/featured/', views.featured_products, name='featured_products'),
    path('products/new/', views.new_products, name='new_products'),
    path('products/bestseller/', views.bestseller_products, name='bestseller_products'),
    
    # Product detail
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Category products
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    
    # Brand products
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    
    # Search
    path('search/', views.search_products, name='search_products'),
    
    # API endpoints for AJAX
    path('api/products/', views.get_products_json, name='get_products_json'),
    path('api/categories/', views.get_categories_json, name='get_categories_json'),
    path('api/brands/', views.get_brands_json, name='get_brands_json'),
    
    # Test view
    path('test/', views.test_products, name='test_products'),
] 