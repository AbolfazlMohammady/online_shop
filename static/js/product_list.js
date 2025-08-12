// Filter functionality
function toggleCompact() {
    const panel = document.getElementById('filter-panel');
    panel.classList.toggle('translate-x-full');
}

// Add working cart functionality from home.html
async function postJson(url, data) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrfToken() },
    body: new URLSearchParams(data)
  });
  return resp.json();
}

function getCsrfToken() {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

async function addToCartHome(productId, btn) {
  const old = btn.innerHTML;
  try {
    btn.disabled = true;
    
    // Use localStorage instead of API to avoid CSRF issues
    addToCartLocalFromCard(productId, btn);
    
    btn.innerHTML = '<i class="fas fa-check"></i>';
    setTimeout(() => { btn.innerHTML = old; btn.disabled = false; }, 1200);
  } catch(e) {
    console.error('Error adding to cart:', e);
    btn.disabled = false;
  }
}

function addToCartLocalFromCard(productId, btn) {
  try {
    const card = btn.closest('a, .theme-card, .product-card') || document;
    const name = card.querySelector('h4, .product-title')?.textContent?.trim() || 'محصول';
    const priceText = (card.querySelector('.text-purple-600, .current-price')?.textContent || '').replace(/[^\d]/g, '') || '0';
    const price = parseInt(priceText) || 0;
    const imgEl = card.querySelector('img');
    const image = imgEl ? imgEl.getAttribute('src') : null;
    const raw = localStorage.getItem('cart') || '[]';
    const cart = JSON.parse(raw);
    const existing = cart.find(it => it.id === productId);
    
    // Check if we have product data from main.js for stock validation
    const product = window.products ? window.products.find(p => p.id === productId) : null;
    if (product) {
      const stockQuantity = parseInt(product.stock_quantity) || 0;
      const currentQuantity = existing ? existing.quantity : 0;
      
      if (stockQuantity <= 0) {
        showNotification(`محصول "${product.name}" موجود نیست. موجودی: ${stockQuantity} عدد`, 'error');
        return;
      }
      
      if (currentQuantity >= stockQuantity) {
        showNotification(`موجودی محصول "${product.name}" کافی نیست. موجودی: ${stockQuantity} عدد`, 'error');
        return;
      }
    }
    
    if (existing) {
      existing.quantity += 1;
      pulseCartCount(cart.reduce((t, it) => t + it.quantity, 0));
      showNotification(`تعداد ${name} به ${existing.quantity} عدد افزایش یافت!`);
    } else {
      cart.push({ 
        id: productId, 
        name, 
        price, 
        quantity: 1, 
        image, 
        color: 'from-pink-200 to-purple-200', 
        iconColor: 'text-gray-400' 
      });
      pulseCartCount(cart.reduce((t, it) => t + it.quantity, 0));
      showNotification(`${name} به سبد خرید اضافه شد!`);
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
  } catch(error) {
    console.error('Error adding to cart:', error);
    showNotification('خطا در افزودن به سبد خرید', 'error');
  }
}

function pulseCartCount(newCount) {
  const el = document.getElementById('cart-count');
  if (!el) return;
  if (typeof newCount === 'number') el.textContent = newCount;
  el.classList.add('animate-pulse');
  setTimeout(() => el.classList.remove('animate-pulse'), 600);
}

function showNotification(message, type = 'info') {
  // Use existing notification system if available
  if (typeof window.showNotification === 'function') {
    window.showNotification(message, type);
  } else {
    alert(message);
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

function openProductDetail(productId) {
    window.location.href = `/shop/product/${productId}/`;
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
    
    // Add event listeners for cart buttons
    document.querySelectorAll('.cart-button').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = parseInt(this.getAttribute('data-product-id'));
            // Use the addToCart function from main.js
            if (typeof window.addToCart === 'function') {
                window.addToCart(productId, e);
            } else {
                addToCartHome(productId, this);
            }
        });
    });
    
    // Add event listeners for wishlist buttons
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            // Use the addToWishlist function from main.js
            if (typeof window.addToWishlist === 'function') {
                window.addToWishlist(productId, e);
            } else {
                toggleWishlistHome(productId, this);
            }
        });
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

async function toggleWishlistHome(productId, btn) {
  try {
    btn.disabled = true;
    const res = await postJson('{% url "shop:toggle_wishlist" %}', { product_id: productId });
    const icon = btn.querySelector('i');
    if (res.added) { icon.classList.remove('far'); icon.classList.add('fas'); }
    else { icon.classList.remove('fas'); icon.classList.add('far'); }
    btn.disabled = false;
  } catch(e) { btn.disabled = false; }
}

// Add missing functions
let activeFilters = {
    search: '',
    category: '',
    brand: '',
    sort: 'default',
    minPrice: null,
    maxPrice: null,
    quickFilter: null
};

function formatPriceInput(input) {
    // Remove non-numeric characters
    let value = input.value.replace(/[^\d]/g, '');
    
    // Add commas for thousands
    if (value) {
        value = parseInt(value).toLocaleString('fa-IR');
    }
    
    input.value = value;
}

function applyPriceFilters() {
    const minPrice = document.getElementById('min-price').value.replace(/[^\d]/g, '');
    const maxPrice = document.getElementById('max-price').value.replace(/[^\d]/g, '');
    
    activeFilters.minPrice = minPrice ? parseInt(minPrice) : null;
    activeFilters.maxPrice = maxPrice ? parseInt(maxPrice) : null;
    
    filterProducts();
}

function filterProducts() {
    // This is a placeholder - the actual filtering logic would be implemented here
    console.log('Filtering products with:', activeFilters);
    // In a real implementation, this would make an AJAX call to get filtered products
}

function setCategoryFilter(category) {
    activeFilters.category = category;
    filterProducts();
}

function setBrandFilter(brand) {
    activeFilters.brand = brand;
    filterProducts();
}

function quickFilter(type) {
    activeFilters.quickFilter = type;
    filterProducts();
}
