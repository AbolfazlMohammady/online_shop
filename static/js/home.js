// Home Page JavaScript Functions

// Banner countdown timer functionality
class BannerCountdown {
    constructor(elementId, endTime) {
        this.element = document.getElementById(elementId);
        this.endTime = new Date(endTime).getTime();
        this.interval = null;
        this.init();
    }

    init() {
        if (!this.element) return;
        this.updateTimer();
        this.interval = setInterval(() => this.updateTimer(), 1000);
    }

    updateTimer() {
        const now = new Date().getTime();
        const distance = this.endTime - now;

        if (distance < 0) {
            // Hide the countdown and show expired message
            const countdownContainer = document.getElementById('countdown-timer-hero');
            if (countdownContainer) {
                countdownContainer.innerHTML = '<span style="color: #fbbf24; font-weight: bold;">تخفیف به پایان رسید!</span>';
            }
            clearInterval(this.interval);
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update only the time values, not the entire structure
        const daysElement = document.getElementById('days-hero');
        const hoursElement = document.getElementById('hours-hero');
        const minutesElement = document.getElementById('minutes-hero');
        const secondsElement = document.getElementById('seconds-hero');
        
        if (daysElement) daysElement.textContent = days.toString().padStart(2, '0');
        if (hoursElement) hoursElement.textContent = hours.toString().padStart(2, '0');
        if (minutesElement) minutesElement.textContent = minutes.toString().padStart(2, '0');
        if (secondsElement) secondsElement.textContent = seconds.toString().padStart(2, '0');
    }

    destroy() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}

// Wishlist functionality
class WishlistManager {
    constructor() {
        this.init();
    }

    async init() {
        this.bindEvents();
        
        // Watch for new wishlist buttons being added to the DOM
        this.observeNewButtons();
    }
    
    observeNewButtons() {
        // Use MutationObserver to watch for new wishlist buttons
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const wishlistBtns = node.querySelectorAll ? node.querySelectorAll('.wishlist-btn') : [];
                        wishlistBtns.forEach(btn => {
                            btn.addEventListener('click', this.handleWishlistClick.bind(this));
                        });
                        
                        // If the node itself is a wishlist button
                        if (node.classList && node.classList.contains('wishlist-btn')) {
                            node.addEventListener('click', this.handleWishlistClick.bind(this));
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    bindEvents() {
        // Remove existing event listeners to avoid duplicates
        document.querySelectorAll('.wishlist-btn').forEach(btn => {
            btn.removeEventListener('click', this.handleWishlistClick);
        });
        
        // Add event listeners to all wishlist buttons
        document.querySelectorAll('.wishlist-btn').forEach(btn => {
            btn.addEventListener('click', this.handleWishlistClick.bind(this));
        });
    }
    
    handleWishlistClick(e) {
        e.preventDefault();
        e.stopPropagation();
        const productId = e.target.closest('.wishlist-btn').getAttribute('data-product-id');
        this.toggleWishlist(productId, e.target.closest('.wishlist-btn'));
    }

    async toggleWishlist(productId, btn) {
        try {
            btn.disabled = true;
            const response = await this.postJson('/shop/api/toggle-wishlist/', { 
                product_id: productId 
            });
            
            const icon = btn.querySelector('i');
            if (response.added) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.showNotification(`محصول به لیست علاقه‌مندی اضافه شد!`, 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.showNotification(`محصول از لیست علاقه‌مندی حذف شد!`, 'info');
            }
        } catch (error) {
            console.error('Error toggling wishlist:', error);
            this.showNotification('خطا در بروزرسانی لیست علاقه‌مندی', 'error');
        } finally {
            btn.disabled = false;
        }
    }

    async postJson(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: new URLSearchParams(data)
        });
        return response.json();
    }

    getCsrfToken() {
        const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'warning' ? 'bg-yellow-500 text-white' : 
            type === 'info' ? 'bg-blue-500 text-white' :
            'bg-green-500 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 
                                type === 'warning' ? 'fa-exclamation-triangle' : 
                                type === 'info' ? 'fa-info-circle' :
                                'fa-check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Cart functionality
class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.querySelectorAll('.cart-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const productId = parseInt(btn.getAttribute('data-product-id'));
                this.addToCart(productId, btn);
            });
        });
    }

    async addToCart(productId, btn) {
        try {
            const oldContent = btn.innerHTML;
            btn.disabled = true;
            
            // Add to cart using localStorage
            this.addToCartLocal(productId, btn);
            
            btn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                btn.innerHTML = oldContent;
                btn.disabled = false;
            }, 1200);
        } catch (error) {
            console.error('Error adding to cart:', error);
            btn.disabled = false;
        }
    }

    addToCartLocal(productId, btn) {
        try {
            // Try to get product data from window.products (from main.js) first
            let productData = null;
            if (window.products && Array.isArray(window.products)) {
                productData = window.products.find(p => p.id === productId);
            }
            
            const card = btn.closest('.theme-card, .product-card') || document;
            
            // Extract product information - prefer API data over HTML extraction
            let name, price, image;
            
            if (productData) {
                // Use API data if available
                name = productData.name;
                price = Number(productData.price);
                image = productData.images && productData.images.length > 0 ? productData.images[0].image : null;
            } else {
                // Fallback to HTML extraction
                name = this.extractProductName(card);
                price = this.extractProductPrice(card);
                image = this.extractProductImage(card);
            }
            
            const raw = localStorage.getItem('cart') || '[]';
            const cart = JSON.parse(raw);
            const existing = cart.find(item => item.id === productId);
            
            if (existing) {
                existing.quantity += 1;
                this.showNotification(`تعداد ${name} به ${existing.quantity} عدد افزایش یافت!`);
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
                this.showNotification(`${name} به سبد خرید اضافه شد!`);
            }
            
            localStorage.setItem('cart', JSON.stringify(cart));
            this.updateCartCount();
            this.pulseCartCount();
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showNotification('خطا در افزودن به سبد خرید', 'error');
        }
    }

    extractProductName(card) {
        let name = card.querySelector('h4, .product-title')?.textContent?.trim();
        if (!name) {
            const parentCard = card.closest('.theme-card');
            if (parentCard) {
                name = parentCard.querySelector('h4')?.textContent?.trim() || 'محصول';
            } else {
                name = 'محصول';
            }
        }
        return name;
    }

    extractProductPrice(card) {
        // Try multiple selectors for price
        const priceSelectors = [
            '.current-price',
            '.text-purple-600', 
            '.product-price .current-price',
            '.product-price span:first-child'
        ];
        
        let priceText = '';
        for (const selector of priceSelectors) {
            const priceEl = card.querySelector(selector);
            if (priceEl && priceEl.textContent) {
                priceText = priceEl.textContent.trim();
                break;
            }
        }
        
        if (!priceText) {
            const parentCard = card.closest('.theme-card, .product-card');
            if (parentCard) {
                for (const selector of priceSelectors) {
                    const priceEl = parentCard.querySelector(selector);
                    if (priceEl && priceEl.textContent) {
                        priceText = priceEl.textContent.trim();
                        break;
                    }
                }
            }
        }
        
        if (!priceText) {
            priceText = '0';
        }
        
        const price = parseInt(priceText.replace(/[^\d]/g, '')) || 0;
        return price;
    }

    extractProductImage(card) {
        let image = null;
        const imgEl = card.querySelector('img');
        if (imgEl) {
            image = imgEl.getAttribute('src');
        } else {
            const parentCard = card.closest('.theme-card');
            if (parentCard) {
                const parentImg = parentCard.querySelector('img');
                if (parentImg) {
                    image = parentImg.getAttribute('src');
                }
            }
        }
        return image;
    }

    updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const count = cart.reduce((total, item) => total + item.quantity, 0);
        const countElement = document.getElementById('cart-count');
        if (countElement) {
            countElement.textContent = count;
        }
    }

    pulseCartCount() {
        const element = document.getElementById('cart-count');
        if (!element) return;
        element.classList.add('animate-pulse');
        setTimeout(() => element.classList.remove('animate-pulse'), 600);
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'warning' ? 'bg-yellow-500 text-white' : 
            type === 'info' ? 'bg-blue-500 text-white' :
            'bg-green-500 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 
                                type === 'warning' ? 'fa-exclamation-triangle' : 
                                type === 'info' ? 'fa-info-circle' :
                                'fa-check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize wishlist manager and make it globally available
    window.wishlistManager = new WishlistManager();
    
    // Initialize cart manager
    new CartManager();
    
    // Initialize banner countdown if banner exists
    const bannerElement = document.getElementById('countdown-timer-hero');
    if (bannerElement && bannerElement.dataset.endTime) {
        new BannerCountdown('countdown-timer-hero', bannerElement.dataset.endTime);
    }
});

// Global functions for backward compatibility
window.addToCart = function(productId) {
    const btn = document.querySelector(`.cart-button[data-product-id="${productId}"]`);
    if (btn) {
        const cartManager = new CartManager();
        cartManager.addToCart(productId, btn);
    }
};

window.toggleWishlistHome = function(productId, btn) {
    const wishlistManager = new WishlistManager();
    wishlistManager.toggleWishlist(productId, btn);
};

// مدیریت حالت تاریک/روشن و انیمیشن فوتر
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    // بررسی حالت ذخیره شده
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        html.classList.add('dark');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<span class="text-xl">☀️</span>';
        }
    }
    
    // تغییر حالت
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            html.classList.toggle('dark');
            
            if (html.classList.contains('dark')) {
                localStorage.setItem('theme', 'dark');
                this.innerHTML = '<span class="text-xl">☀️</span>';
            } else {
                localStorage.setItem('theme', 'light');
                this.innerHTML = '<span class="text-xl">🌙</span>';
            }
        });
    }
    
    // انیمیشن آیکون‌های اجتماعی
    const socialIcons = document.querySelectorAll('.social-icon');
    
    socialIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});