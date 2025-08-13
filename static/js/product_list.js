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
    // Find the product card that contains the button
    const productCard = btn.closest('.product-card') || btn.closest('.theme-card') || btn.closest('.product-item');
    if (!productCard) {
      console.error('Product card not found for button:', btn);
      console.log('Button parent elements:', btn.parentElement);
      return;
    }
    
    console.log('Found product card:', productCard);
    
    // Try multiple selectors for product name
    const nameSelectors = ['h3', '.product-name', 'h4', '.product-title', '.title'];
    let name = 'محصول';
    for (const selector of nameSelectors) {
      const nameEl = productCard.querySelector(selector);
      if (nameEl && nameEl.textContent.trim()) {
        name = nameEl.textContent.trim();
        console.log('Found product name:', name);
        break;
      }
    }
    
    // Try multiple selectors for product price
    const priceSelectors = ['.product-price', '.text-purple-600', '.current-price', '.price'];
    let price = 0;
    for (const selector of priceSelectors) {
      const priceEl = productCard.querySelector(selector);
      if (priceEl && priceEl.textContent) {
        const priceText = priceEl.textContent.replace(/[^\d]/g, '');
        if (priceText) {
          price = parseInt(priceText);
          console.log('Found product price:', price);
          break;
        }
      }
    }
    
    const imgEl = productCard.querySelector('img');
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

// Removed local addToWishlist function - now using home page's WishlistManager

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
            e.stopPropagation();
            const productId = parseInt(this.getAttribute('data-product-id'));
            console.log('Cart button clicked, productId:', productId);
            
            // Use the addToCart function from main.js
            if (typeof window.addToCart === 'function') {
                window.addToCart(productId, e);
            } else {
                addToCartHome(productId, this);
            }
        });
    });
    
    // Wishlist buttons are handled by WishlistManager from home.js
    // No need to add event listeners here as they're handled globally
    
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
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize price inputs
    initializePriceInputs();
    
    // Initialize filter buttons
    initializeFilterButtons();
    
    // Initialize filter pills
    initializeFilterPills();
    
    // Load initial products
    loadProducts();
    
    // Update cart count
    updateCartCount();
});

function clearFilters() {
    console.log('Clearing all filters');
    
    // Reset all form elements
    const searchInput = document.getElementById('search-input');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const sortFilter = document.getElementById('sort-filter');
    const categoryFilter = document.getElementById('category-filter');
    const brandFilter = document.getElementById('brand-filter');
    
    if (searchInput) searchInput.value = '';
    if (minPriceInput) minPriceInput.value = '';
    if (maxPriceInput) maxPriceInput.value = '';
    if (sortFilter) sortFilter.value = 'default';
    if (categoryFilter) categoryFilter.value = '';
    if (brandFilter) brandFilter.value = '';
    
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

// Removed toggleWishlistHome function - now using WishlistManager from home.js

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
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    
    if (!minPriceInput || !maxPriceInput) {
        console.error('Price input elements not found');
        return;
    }
    
    const minPrice = minPriceInput.value.replace(/[^\d]/g, '');
    const maxPrice = maxPriceInput.value.replace(/[^\d]/g, '');
    
    activeFilters.minPrice = minPrice ? parseInt(minPrice) : null;
    activeFilters.maxPrice = maxPrice ? parseInt(maxPrice) : null;
    
    console.log('Applying price filters:', activeFilters);
    filterProducts();
}

function filterProducts() {
    console.log('Filtering products with:', activeFilters);
    
    // Get all product cards
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        let shouldShow = true;
        
        // Filter by search
        if (activeFilters.search) {
            const productName = card.querySelector('h3, .product-name')?.textContent?.toLowerCase() || '';
            if (!productName.includes(activeFilters.search.toLowerCase())) {
                shouldShow = false;
            }
        }
        
        // Filter by category
        if (activeFilters.category) {
            const productCategory = card.getAttribute('data-category') || '';
            if (productCategory !== activeFilters.category) {
                shouldShow = false;
            }
        }
        
        // Filter by brand
        if (activeFilters.brand) {
            const productBrand = card.getAttribute('data-brand') || '';
            if (productBrand !== activeFilters.brand) {
                shouldShow = false;
            }
        }
        
        // Filter by price
        if (activeFilters.minPrice || activeFilters.maxPrice) {
            const priceElement = card.querySelector('.product-price');
            if (priceElement) {
                const price = parseInt(priceElement.textContent.replace(/[^\d]/g, '')) || 0;
                
                if (activeFilters.minPrice && price < activeFilters.minPrice) {
                    shouldShow = false;
                }
                
                if (activeFilters.maxPrice && price > activeFilters.maxPrice) {
                    shouldShow = false;
                }
            }
        }
        
        // Show/hide card
        if (shouldShow) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Update results count
    const visibleCards = document.querySelectorAll('.product-card:not([style*="display: none"])');
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.textContent = `نمایش ${visibleCards.length} محصول`;
    }
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

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            activeFilters.search = this.value;
            filterProducts();
        });
    }
}

function initializePriceInputs() {
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    
    if (minPriceInput) {
        minPriceInput.addEventListener('input', function() {
            formatPriceInput(this);
        });
    }
    
    if (maxPriceInput) {
        maxPriceInput.addEventListener('input', function() {
            formatPriceInput(this);
        });
    }
}

function loadProducts() {
    // This function would load products from the server
    // For now, we'll just initialize the existing products
    console.log('Loading products...');
    
    // Update cart count
    updateCartCount();
    
    // Initialize filter pills
    initializeFilterPills();
}

function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const countElement = document.getElementById('cart-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

function initializeFilterPills() {
    // Category pills
    document.querySelectorAll('.category-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Remove active class from all category pills
            document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked pill
            this.classList.add('active');
            
            setCategoryFilter(category);
        });
    });
    
    // Brand pills
    document.querySelectorAll('.brand-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            const brand = this.getAttribute('data-brand');
            
            // Remove active class from all brand pills
            document.querySelectorAll('.brand-pill').forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked pill
            this.classList.add('active');
            
            setBrandFilter(brand);
        });
    });
    
    // Quick filter buttons
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filterType = this.getAttribute('data-quick-filter');
            
            // Remove active class from all quick filter buttons
            document.querySelectorAll('.quick-filter-btn').forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            quickFilter(filterType);
        });
    });
}
