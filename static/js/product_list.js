// Filter functionality
function toggleCompact() {
    const panel = document.getElementById('filter-panel');
    panel.classList.toggle('translate-x-full');
}

// Add event listeners for price range
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking buttons...');
    
    // Debug: Check if buttons exist
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    const cartButtons = document.querySelectorAll('.cart-button');
    
    console.log('Found wishlist buttons:', wishlistButtons.length);
    console.log('Found cart buttons:', cartButtons.length);
    
    // Force button visibility
    wishlistButtons.forEach(btn => {
        btn.style.display = 'flex';
        btn.style.opacity = '1';
        btn.style.visibility = 'visible';
        btn.style.zIndex = '999';
        console.log('Wishlist button styles:', btn.style.cssText);
    });
    
    cartButtons.forEach(btn => {
        btn.style.display = 'flex';
        btn.style.opacity = '1';
        btn.style.visibility = 'visible';
        btn.style.zIndex = '999';
        console.log('Cart button styles:', btn.style.cssText);
    });
    
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const applyBtn = document.querySelector('button[onclick="applyFilters()"]');
    const clearBtn = document.querySelector('button[onclick="clearFilters()"]');
    
    // Price inputs - format on input
    if (minPriceInput) {
        minPriceInput.addEventListener('input', formatPriceInput);
    }
    
    if (maxPriceInput) {
        maxPriceInput.addEventListener('input', formatPriceInput);
    }
    
    // Apply button - only for price range
    if (applyBtn) {
        applyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            applyPriceFilters();
        });
    }
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearFilters();
        });
    }
    
    // New button IDs
    const applyPriceBtn = document.getElementById('apply-price-filter');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    
    if (applyPriceBtn) {
        applyPriceBtn.addEventListener('click', function(e) {
            e.preventDefault();
            applyPriceFilters();
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearFilters();
        });
    }
    
    // Sort filter
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            activeFilters.sort = this.value;
            filterProducts();
        });
    }
});

function clearFilters() {
    console.log('Clearing all filters');
    
    // Reset all form elements
    document.getElementById('search-input').value = '';
    document.getElementById('min-price').value = '';
    document.getElementById('max-price').value = '';
    document.getElementById('sort-filter').value = 'default';
    document.getElementById('category-filter').value = '';
    document.getElementById('brand-filter').value = '';
    
    // Reset all filters
    activeFilters = {
        search: '',
        category: '',
        brand: '',
        sort: 'default',
        minPrice: null,
        maxPrice: null,
        quickFilter: null
    };
    
    // Reset all pills and buttons
    document.querySelectorAll('.category-pill, .brand-pill, .quick-filter-btn').forEach(element => {
        element.classList.remove('active');
    });
    
    // Set first pills as active
    const firstCategoryPill = document.querySelector('.category-pill');
    const firstBrandPill = document.querySelector('.brand-pill');
    
    if (firstCategoryPill) firstCategoryPill.classList.add('active');
    if (firstBrandPill) firstBrandPill.classList.add('active');
    
    console.log('Filters cleared, calling filterProducts');
    filterProducts();
}

function addToCart(productId, event) {
    if (event) {
        event.stopPropagation(); // Prevent card click
    }
    
    // Use the main.js addToCart function
    if (typeof window.addToCart === 'function') {
        window.addToCart(productId, event);
    } else {
        // Fallback
        console.log('Adding product to cart:', productId);
        
        // Show success message
        const button = event ? event.target.closest('.cart-button') : null;
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)';
            }, 1500);
        }
    }
}

async function addToWishlist(productId, event) {
    event.stopPropagation(); // Prevent card click
    
    const button = event.target.closest('.wishlist-btn');
    const icon = button.querySelector('i');
    
    try {
        const response = await fetch('/shop/api/toggle-wishlist/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `product_id=${productId}`
        });
        
        const result = await response.json();
        
        if (result.added) {
            // Add to wishlist
            icon.classList.remove('far');
            icon.classList.add('fas');
            button.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
            showNotification('محصول به علاقه‌مندی‌ها اضافه شد!', 'success');
        } else {
            // Remove from wishlist
            icon.classList.remove('fas');
            icon.classList.add('far');
            button.style.background = 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)';
            showNotification('محصول از علاقه‌مندی‌ها حذف شد!', 'info');
        }
    } catch (error) {
        console.error('Error toggling wishlist:', error);
        showNotification('خطا در به‌روزرسانی علاقه‌مندی‌ها', 'error');
    }
}

function getCsrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}

function showNotification(message, type = 'info') {
    // Use existing notification system if available
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        alert(message);
    }
}

function openProductDetail(productId) {
    window.location.href = `/shop/product/${productId}/`;
}
