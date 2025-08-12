from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Product listing and filtering
    path('products/', views.product_list, name='product_list'),
    path('products/featured/', views.featured_products, name='featured_products'),
    path('products/new/', views.new_products, name='new_products'),
    path('products/bestseller/', views.bestseller_products, name='bestseller_products'),
    path('products/most-viewed/', views.most_viewed_products, name='most_viewed_products'),
    
    # Product detail
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
    

    path('product/<int:product_id>/comment/', views.add_comment, name='add_comment'),

    
    # Category products
    path('category/<str:slug>/', views.category_products, name='category_products'),
    
    # Brand products
    path('brand/<str:slug>/', views.brand_products, name='brand_products'),
    
    # Search
    path('search/', views.search_products, name='search_products'),
    
    # API endpoints for AJAX
    path('api/products/', views.get_products_json, name='get_products_json'),
    path('api/categories/', views.get_categories_json, name='get_categories_json'),
    path('api/brands/', views.get_brands_json, name='get_brands_json'),
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    # Cart page
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-order/', views.process_order, name='process_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    # Shipping settings API
    path('api/shipping-settings/', views.get_shipping_settings_api, name='shipping_settings_api'),
    
    # Test view
    path('test/', views.test_products, name='test_products'),
] 