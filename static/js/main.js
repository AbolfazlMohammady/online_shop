// Global variables
let products = []; // Will be populated from API
let filteredProducts = [];
let currentView = 'grid';
let cart = [];
let currentPage = 'home';
let currentFilter = 'all';
let currentSort = 'default';
let currentSearch = '';
let currentPriceRange = { min: 0, max: 1000000 };

// Infinite scroll variables
let currentPageNumber = 1;
let isLoading = false;
let hasMoreProducts = true;
let productsPerPage = 12;

// Load products from API
async function loadProducts(page = 1, append = false) {
    console.log('Loading products page:', page, 'append:', append);
    
    // Prevent multiple simultaneous requests
    if (window.isLoadingProducts) {
        console.log('Products already loading, skipping...');
        return;
    }
    
    window.isLoadingProducts = true;
    
    try {
        const response = await fetch(`/shop/api/products/?page=${page}`);
        const data = await response.json();
        
        console.log('API response:', data);
        
        if (data.products && Array.isArray(data.products)) {
            if (append) {
                // Append new products to existing ones
                products.push(...data.products);
                filteredProducts.push(...data.products);
                console.log('Appended products, total:', products.length);
            } else {
                // Replace all products
                products = data.products;
                filteredProducts = [...data.products];
                console.log('Replaced products, total:', products.length);
            }
            
            // Update pagination state
            hasMoreProducts = data.has_next;
            currentPageNumber = data.current_page;
            
            // Show/hide load more button
            const loadMoreBtn = document.getElementById('load-more-btn');
            const endMessage = document.getElementById('end-message');
            
            if (loadMoreBtn) {
                if (hasMoreProducts) {
                    loadMoreBtn.classList.remove('hidden');
                } else {
                    loadMoreBtn.classList.add('hidden');
                }
            }
            
            if (endMessage) {
                if (!hasMoreProducts && products.length > 0) {
                    endMessage.classList.remove('hidden');
                } else {
                    endMessage.classList.add('hidden');
                }
            }
            
            // Render products
            renderProducts(filteredProducts);
            updateResultsInfo();
            
        } else {
            console.error('Invalid API response format:', data);
        }
        
    } catch (error) {
        console.error('Error loading products:', error);
    } finally {
        window.isLoadingProducts = false;
    }
}

// Sample products data - keeping for fallback
const sampleProducts = [
    {
        id: 1,
        name: 'رژ لب مات قرمز',
        category: 'رژ لب',
        price: 125000,
        rating: 4.8,
        image: 'fas fa-lipstick',
        color: 'from-red-200 to-pink-200',
        iconColor: 'text-red-600',
        tags: ['bestseller', 'discount'],
        detailImages: [
            { color: 'from-red-300 to-pink-300', icon: 'fas fa-lipstick', iconColor: 'text-red-700' },
            { color: 'from-red-100 to-pink-100', icon: 'fas fa-lipstick', iconColor: 'text-red-500' },
            { color: 'from-red-400 to-pink-400', icon: 'fas fa-lipstick', iconColor: 'text-red-800' }
        ]
    },
    {
        id: 2,
        name: 'کرم مرطوب کننده',
        category: 'کرم',
        price: 85000,
        rating: 4.6,
        image: 'fas fa-tint',
        color: 'from-blue-200 to-cyan-200',
        iconColor: 'text-blue-600',
        tags: ['new'],
        detailImages: [
            { color: 'from-blue-300 to-cyan-300', icon: 'fas fa-tint', iconColor: 'text-blue-700' },
            { color: 'from-blue-100 to-cyan-100', icon: 'fas fa-tint', iconColor: 'text-blue-500' },
            { color: 'from-blue-400 to-cyan-400', icon: 'fas fa-tint', iconColor: 'text-blue-800' }
        ]
    },
    {
        id: 3,
        name: 'عطر زنانه گل یاس',
        category: 'عطر',
        price: 250000,
        rating: 4.9,
        image: 'fas fa-spray-can',
        color: 'from-purple-200 to-indigo-200',
        iconColor: 'text-purple-600',
        tags: ['luxury', 'bestseller'],
        detailImages: [
            { color: 'from-purple-300 to-indigo-300', icon: 'fas fa-spray-can', iconColor: 'text-purple-700' },
            { color: 'from-purple-100 to-indigo-100', icon: 'fas fa-spray-can', iconColor: 'text-purple-500' },
            { color: 'from-purple-400 to-indigo-400', icon: 'fas fa-spray-can', iconColor: 'text-purple-800' }
        ]
    },
    {
        id: 4,
        name: 'گیره مو طلایی',
        category: 'گیره مو',
        price: 35000,
        rating: 4.3,
        image: 'fas fa-cut',
        color: 'from-yellow-200 to-orange-200',
        iconColor: 'text-yellow-600',
        tags: ['discount'],
        detailImages: [
            { color: 'from-yellow-300 to-orange-300', icon: 'fas fa-cut', iconColor: 'text-yellow-700' },
            { color: 'from-yellow-100 to-orange-100', icon: 'fas fa-cut', iconColor: 'text-yellow-500' },
            { color: 'from-yellow-400 to-orange-400', icon: 'fas fa-cut', iconColor: 'text-yellow-800' }
        ]
    },
    {
        id: 5,
        name: 'رژ لب صورتی',
        category: 'رژ لب',
        price: 110000,
        rating: 4.7,
        image: 'fas fa-lipstick',
        color: 'from-pink-200 to-rose-200',
        iconColor: 'text-pink-600',
        tags: ['bestseller'],
        detailImages: [
            { color: 'from-pink-300 to-rose-300', icon: 'fas fa-lipstick', iconColor: 'text-pink-700' },
            { color: 'from-pink-100 to-rose-100', icon: 'fas fa-lipstick', iconColor: 'text-pink-500' },
            { color: 'from-pink-400 to-rose-400', icon: 'fas fa-lipstick', iconColor: 'text-pink-800' }
        ]
    },
    {
        id: 6,
        name: 'کرم ضد آفتاب',
        category: 'کرم',
        price: 95000,
        rating: 4.5,
        image: 'fas fa-sun',
        color: 'from-orange-200 to-yellow-200',
        iconColor: 'text-orange-600',
        tags: ['new', 'discount'],
        detailImages: [
            { color: 'from-orange-300 to-yellow-300', icon: 'fas fa-sun', iconColor: 'text-orange-700' },
            { color: 'from-orange-100 to-yellow-100', icon: 'fas fa-sun', iconColor: 'text-orange-500' },
            { color: 'from-orange-400 to-yellow-400', icon: 'fas fa-sun', iconColor: 'text-orange-800' }
        ]
    },
    {
        id: 7,
        name: 'سرم ویتامین C',
        category: 'سرم',
        price: 180000,
        rating: 4.9,
        image: 'fas fa-leaf',
        color: 'from-green-200 to-emerald-200',
        iconColor: 'text-green-600',
        tags: ['luxury', 'new'],
        detailImages: [
            { color: 'from-green-300 to-emerald-300', icon: 'fas fa-leaf', iconColor: 'text-green-700' },
            { color: 'from-green-100 to-emerald-100', icon: 'fas fa-leaf', iconColor: 'text-green-500' },
            { color: 'from-green-400 to-emerald-400', icon: 'fas fa-leaf', iconColor: 'text-green-800' }
        ]
    },
    {
        id: 8,
        name: 'عطر لوکس زنانه',
        category: 'عطر',
        price: 320000,
        rating: 4.8,
        image: 'fas fa-gem',
        color: 'from-indigo-200 to-purple-200',
        iconColor: 'text-indigo-600',
        tags: ['luxury'],
        detailImages: [
            { color: 'from-indigo-300 to-purple-300', icon: 'fas fa-gem', iconColor: 'text-indigo-700' },
            { color: 'from-indigo-100 to-purple-100', icon: 'fas fa-gem', iconColor: 'text-indigo-500' },
            { color: 'from-indigo-400 to-purple-400', icon: 'fas fa-gem', iconColor: 'text-indigo-800' }
        ]
    }
];

let activeFilters = {
    search: '',
    category: '',
    brand: '',
    sort: 'default',
    minPrice: null,
    maxPrice: null,
    quickFilter: null
};

// Countdown Timer Function - تایمر شمارش معکوس
function startCountdown() {
    const countdownDate = new Date().getTime() + (24 * 60 * 60 * 1000);
    
    const timer = setInterval(function() {
        const now = new Date().getTime();
        const distance = countdownDate - now;
        
        if (distance < 0) {
            clearInterval(timer);
            const timerElement = document.getElementById('countdown-timer-hero');
            if (timerElement) {
                timerElement.innerHTML = '<span class="text-yellow-300">⏰ تخفیف به پایان رسید!</span>';
            }
            return;
        }
        
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        const hoursEl = document.getElementById('hours-hero');
        const minutesEl = document.getElementById('minutes-hero');
        const secondsEl = document.getElementById('seconds-hero');
        
        if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, '0');
        if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, '0');
        if (secondsEl) secondsEl.textContent = seconds.toString().padStart(2, '0');
    }, 1000);
}

// Page Navigation
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    currentPage = pageId;
    
    // Update desktop navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('text-purple-600', 'bg-purple-50', 'dark:bg-purple-900/20');
        const underline = link.querySelector('span');
        if (underline) {
            underline.classList.remove('w-full');
            underline.classList.add('w-0');
        }
        if (link.dataset.page === pageId) {
            link.classList.add('text-purple-600', 'bg-purple-50', 'dark:bg-purple-900/20');
            if (underline) {
                underline.classList.remove('w-0');
                underline.classList.add('w-full');
            }
        }
    });
    
    // Update mobile navigation
    updateMobileNav(pageId);
    
    // Update URL hash
    window.location.hash = pageId;
    
    // Scroll to top
    window.scrollTo(0, 0);
    
    // Page-specific actions
    if (pageId === 'products') {
        // Load products from API if not already loaded
        if (products.length === 0) {
            loadProducts();
        } else {
            renderProducts(filteredProducts);
            updateResultsInfo();
        }
    } else if (pageId === 'blog') {
        renderBlogs();
    } else if (pageId === 'cart') {
        renderCart();
    }
}

// Set active navigation link
function setActiveNavLink(clickedLink) {
    // Remove active state from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('text-purple-600', 'bg-purple-50', 'dark:bg-purple-900/20');
        const underline = link.querySelector('span');
        if (underline) {
            underline.classList.remove('w-full');
            underline.classList.add('w-0');
        }
    });
    
    // Add active state to clicked link
    clickedLink.classList.add('text-purple-600', 'bg-purple-50', 'dark:bg-purple-900/20');
    const underline = clickedLink.querySelector('span');
    if (underline) {
        underline.classList.remove('w-0');
        underline.classList.add('w-full');
    }
}

// Filter by category
function filterByCategory(category) {
    // Map category names to product categories
    const categoryMap = {
        'آرایش صورت': ['رژ لب'],
        'مراقبت پوست': ['کرم'],
        'مراقبت مو': ['مراقبت مو'],
        'عطر': ['عطر'],
        'گیره مو': ['گیره مو']
    };
    
    const targetCategories = categoryMap[category] || [category];
    
    // Filter and render products
    const filteredProducts = products.filter(product => 
        targetCategories.includes(product.category)
    );
    
    renderProducts(filteredProducts);
    
    // Set active nav link for products page
    const productsLink = document.querySelector('[data-page="products"]');
    if (productsLink) {
        setActiveNavLink(productsLink);
    }
}

// Mobile Navigation
function updateMobileNav(activePageId) {
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === activePageId) {
            item.classList.add('active');
        }
    });
}

// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    
    body.classList.toggle('dark');
    
    if (body.classList.contains('dark')) {
        icon.className = 'fas fa-sun text-lg';
        localStorage.setItem('theme', 'dark');
    } else {
        icon.className = 'fas fa-moon text-lg';
        localStorage.setItem('theme', 'light');
    }
}

let previousPage = 'home';

// Product Detail Functions
function showProductDetail(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    previousPage = getCurrentPage();
    
    const detailContent = document.getElementById('product-detail-content');
    detailContent.innerHTML = `
        <!-- Product Image -->
        <div class="space-y-6">
            <div class="aspect-square bg-gradient-to-br ${product.color} rounded-2xl flex items-center justify-center shadow-lg">
                <i class="${product.image} text-8xl ${product.iconColor}"></i>
            </div>
            
            <!-- Product Gallery Thumbnails -->
            <div class="flex gap-3">
                <div class="w-20 h-20 bg-gradient-to-br ${product.color} rounded-xl flex items-center justify-center border-2 border-purple-500 cursor-pointer">
                    <i class="${product.image} text-2xl ${product.iconColor}"></i>
                </div>
                <div class="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-xl flex items-center justify-center cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
                    <i class="${product.image} text-2xl text-gray-500"></i>
                </div>
                <div class="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-xl flex items-center justify-center cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
                    <i class="${product.image} text-2xl text-gray-500"></i>
                </div>
            </div>
        </div>
        
        <!-- Product Info -->
        <div class="space-y-8">
            <div>
                <h1 class="text-4xl font-bold mb-4 text-gray-900 dark:text-white">${product.name}</h1>
                <p class="text-lg text-gray-900 dark:text-gray-400 mb-6">دسته‌بندی: ${product.category}</p>
                
                <!-- Rating -->
                <div class="flex items-center gap-4 mb-6">
                    <div class="flex text-yellow-400 text-lg">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                    </div>
                    <span class="text-lg font-semibold text-gray-900 dark:text-white">${product.rating}</span>
                    <span class="text-gray-900 dark:text-gray-400">(۱۲۳ نظر)</span>
                </div>
                
                <!-- Price -->
                <div class="flex items-center gap-4 mb-8">
                    <span class="text-3xl font-bold text-purple-600">${product.price.toLocaleString()} تومان</span>
                    <span class="text-lg text-gray-900 dark:text-gray-400 line-through">${(product.price * 1.2).toLocaleString()} تومان</span>
                    <span class="bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 px-3 py-1 rounded-lg text-sm font-bold">۲۰٪ تخفیف</span>
                </div>
            </div>
            
            <!-- Product Options -->
            <div class="space-y-6">
                <div>
                    <h3 class="text-lg font-bold mb-3 text-gray-900 dark:text-white">رنگ:</h3>
                    <div class="flex gap-3">
                        <button class="w-12 h-12 bg-red-500 rounded-full border-2 border-purple-500 shadow-lg"></button>
                        <button class="w-12 h-12 bg-pink-500 rounded-full border-2 border-transparent hover:border-purple-500 shadow-lg transition-colors"></button>
                        <button class="w-12 h-12 bg-purple-500 rounded-full border-2 border-transparent hover:border-purple-500 shadow-lg transition-colors"></button>
                    </div>
                </div>
                
                <div>
                    <h3 class="text-lg font-bold mb-3 text-gray-900 dark:text-white">تعداد:</h3>
                    <div class="flex items-center gap-4">
                        <button class="w-12 h-12 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-xl flex items-center justify-center font-bold text-lg transition-colors text-gray-900 dark:text-gray-300">-</button>
                        <span class="text-xl font-bold w-12 text-center text-gray-900 dark:text-white">1</span>
                        <button class="w-12 h-12 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-xl flex items-center justify-center font-bold text-lg transition-colors text-gray-900 dark:text-gray-300">+</button>
                    </div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="space-y-4">
                <button onclick="addToCart(${product.id})" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-4 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-3">
                    <i class="fas fa-cart-plus"></i>
                    افزودن به سبد خرید
                </button>
                <button class="w-full bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 py-4 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-3 text-gray-900 dark:text-gray-300">
                    <i class="fas fa-heart"></i>
                    افزودن به علاقه‌مندی‌ها
                </button>
            </div>
            
            <!-- Product Description -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">توضیحات محصول</h3>
                <p class="leading-relaxed text-gray-900 dark:text-gray-300 mb-6">
                    این محصول با کیفیت بالا و مواد اولیه درجه یک تولید شده است. مناسب برای استفاده روزانه و دارای ماندگاری بالا می‌باشد. 
                    تمامی محصولات ما دارای مجوزهای لازم و تست شده توسط متخصصان هستند.
                </p>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check-circle text-green-500"></i>
                        <span class="text-gray-900 dark:text-white font-medium">کیفیت تضمینی</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check-circle text-green-500"></i>
                        <span class="text-gray-900 dark:text-white font-medium">ارسال سریع</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check-circle text-green-500"></i>
                        <span class="text-gray-900 dark:text-white font-medium">ضمانت بازگشت</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check-circle text-green-500"></i>
                        <span class="text-gray-900 dark:text-white font-medium">پشتیبانی ۲۴/۷</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showPage('product-detail');
}

// Blog Detail Functions
function showBlogDetail(blogId) {
    const blog = blogs.find(b => b.id === blogId);
    if (!blog) return;
    
    previousPage = getCurrentPage();
    
    const detailContent = document.getElementById('blog-detail-content');
    detailContent.innerHTML = `
        <article class="theme-bg rounded-2xl shadow-lg overflow-hidden">
            <!-- Blog Header -->
            <div class="h-64 bg-gradient-to-br ${blog.color} flex items-center justify-center">
                <i class="${blog.image} text-6xl ${blog.iconColor}"></i>
            </div>
            
            <!-- Blog Content -->
            <div class="p-8">
                ${blog.content}
                
                <!-- Share Buttons -->
                <div class="mt-12 pt-8 border-t theme-border">
                    <h4 class="text-lg font-bold mb-4">اشتراک‌گذاری:</h4>
                    <div class="flex gap-3">
                        <button class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                            <i class="fab fa-telegram"></i>
                            تلگرام
                        </button>
                        <button class="flex items-center gap-2 bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg transition-colors">
                            <i class="fab fa-instagram"></i>
                            اینستاگرام
                        </button>
                        <button class="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors">
                            <i class="fab fa-whatsapp"></i>
                            واتساپ
                        </button>
                    </div>
                </div>
                
                <!-- Related Posts -->
                <div class="mt-12 pt-8 border-t theme-border">
                    <h4 class="text-lg font-bold mb-6">مطالب مرتبط:</h4>
                    <div class="grid md:grid-cols-2 gap-6">
                        ${blogs.filter(b => b.id !== blogId).slice(0, 2).map(relatedBlog => `
                            <div onclick="showBlogDetail(${relatedBlog.id})" class="flex gap-4 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors">
                                <div class="w-16 h-16 bg-gradient-to-br ${relatedBlog.color} rounded-xl flex items-center justify-center flex-shrink-0">
                                    <i class="${relatedBlog.image} text-xl ${relatedBlog.iconColor}"></i>
                                </div>
                                <div>
                                    <h5 class="font-bold mb-1">${relatedBlog.title}</h5>
                                    <p class="text-sm theme-text-secondary">${relatedBlog.date}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </article>
    `;
    
    showPage('blog-detail');
}

// Helper Functions
function getCurrentPage() {
    const activePage = document.querySelector('.page.active');
    return activePage ? activePage.id : 'home';
}

function goBack() {
    showPage(previousPage);
}

// Render Blog Posts
function renderBlogs() {
    const blogGrid = document.getElementById('blog-grid');
    if (!blogGrid) return;
    
    blogGrid.innerHTML = blogs.map(blog => `
        <article onclick="openBlogModal(${blog.id})" class="theme-card rounded-xl shadow-lg overflow-hidden card-hover cursor-pointer">
            <div class="h-24 sm:h-32 bg-gradient-to-br ${blog.color} flex items-center justify-center">
                <i class="${blog.image} text-lg sm:text-2xl ${blog.iconColor}"></i>
            </div>
            <div class="p-2 sm:p-4">
                <h3 class="text-xs sm:text-base font-bold mb-1 sm:mb-2 line-clamp-2">${blog.title}</h3>
                <p class="theme-text-secondary text-xs mb-2 sm:mb-3 line-clamp-3">${blog.excerpt}</p>
                <div class="flex items-center justify-between">
                    <span class="text-xs theme-text-secondary">${blog.date}</span>
                    <button class="text-purple-600 hover:text-purple-700 font-semibold text-xs">ادامه مطلب</button>
                </div>
            </div>
        </article>
    `).join('');
}

// Products Functions
function renderProducts(productsToRender = products) {
    console.log('Rendering products:', productsToRender.length, 'in view:', currentView);
    
    const grid = document.getElementById('products-grid');
    if (!grid) {
        console.error('Products grid not found!');
        return;
    }
    
    // Clear existing content
    grid.innerHTML = '';
    
    if (productsToRender.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <div class="text-gray-400 mb-4">
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <h3 class="text-lg font-semibold mb-2">هیچ محصولی یافت نشد</h3>
                    <p class="text-sm">لطفاً فیلترهای خود را تغییر دهید یا عبارت جستجوی دیگری را امتحان کنید.</p>
                    </div>
                </div>
            `;
        return;
    }
    
    // Set grid class based on current view
    if (currentView === 'list') {
        grid.className = 'space-y-4';
        renderListView(productsToRender, grid);
    } else {
        grid.className = 'products-grid';
        renderGridView(productsToRender, grid);
    }
    
    console.log('Products rendered successfully in', currentView, 'view');
}

// Cart Functions
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1,
            image: product.images && product.images.length > 0 ? product.images[0].image : null,
            color: 'from-pink-200 to-purple-200',
            iconColor: 'text-gray-400'
        });
    }
    
    updateCartCount();
    renderCart();
    showNotification('محصول به سبد خرید اضافه شد!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartCount();
    renderCart();
}

function updateQuantity(productId, newQuantity) {
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = newQuantity;
        updateCartCount();
        renderCart();
    }
}

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    document.getElementById('cart-count').textContent = count;
}

function renderCart() {
    const cartItems = document.getElementById('cart-items');
    if (!cartItems) return;
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="text-center py-8 sm:py-12">
                <i class="fas fa-shopping-cart text-4xl sm:text-6xl text-gray-300 mb-3 sm:mb-4"></i>
                <h3 class="text-lg sm:text-xl font-bold mb-2 text-gray-900 dark:text-white">سبد خرید شما خالی است</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4 sm:mb-6 text-sm sm:text-base">برای خرید محصولات به صفحه محصولات بروید</p>
                <button onclick="showPage('products')" class="bg-purple-600 hover:bg-purple-700 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg sm:rounded-xl font-semibold transition-colors text-sm sm:text-base">
                    مشاهده محصولات
                </button>
            </div>
        `;
    } else {
        cartItems.innerHTML = cart.map(item => `
            <div class="flex items-center gap-2 sm:gap-4 p-3 sm:p-4 border border-gray-200 dark:border-gray-700 rounded-lg sm:rounded-xl bg-white dark:bg-gray-800 shadow-sm">
                <div class="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br ${item.color} rounded-lg sm:rounded-xl flex items-center justify-center flex-shrink-0">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" class="w-full h-full object-cover rounded-lg sm:rounded-xl">` : `<i class="fas fa-image text-lg sm:text-xl ${item.iconColor}"></i>`}
                </div>
                <div class="flex-1 min-w-0">
                    <h4 class="font-bold text-sm sm:text-base line-clamp-1 text-gray-900 dark:text-white">${item.name}</h4>
                    <p class="text-purple-600 font-semibold text-xs sm:text-sm">${item.price.toLocaleString()} تومان</p>
                </div>
                <div class="flex items-center gap-1 sm:gap-3">
                    <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})" class="w-6 h-6 sm:w-8 sm:h-8 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-full flex items-center justify-center transition-colors">
                        <i class="fas fa-minus text-xs text-gray-700 dark:text-gray-300"></i>
                    </button>
                    <span class="w-6 sm:w-8 text-center font-semibold text-sm sm:text-base text-gray-900 dark:text-white">${item.quantity}</span>
                    <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})" class="w-6 h-6 sm:w-8 sm:h-8 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-full flex items-center justify-center transition-colors">
                        <i class="fas fa-plus text-xs text-gray-700 dark:text-gray-300"></i>
                    </button>
                </div>
                <button onclick="removeFromCart(${item.id})" class="text-red-600 hover:text-red-700 p-1 sm:p-2 transition-colors">
                    <i class="fas fa-trash text-sm"></i>
                </button>
            </div>
        `).join('');
    }
    
    updateCartSummary();
}

function updateCartSummary() {
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    const shipping = subtotal > 500000 ? 0 : 25000;
    const discount = 10000;
    const total = subtotal + shipping - discount;
    
    const subtotalEl = document.getElementById('subtotal');
    const shippingEl = document.getElementById('shipping');
    const totalEl = document.getElementById('total');
    
    if (subtotalEl) subtotalEl.textContent = subtotal.toLocaleString() + ' تومان';
    if (shippingEl) shippingEl.textContent = shipping === 0 ? 'رایگان' : shipping.toLocaleString() + ' تومان';
    if (totalEl) totalEl.textContent = total.toLocaleString() + ' تومان';
}

function checkout() {
    if (cart.length === 0) {
        showNotification('سبد خرید شما خالی است!');
        return;
    }
    showNotification('در حال انتقال به درگاه پرداخت...');
}

// Notification Function
function showNotification(message, type = 'success') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.className = `${colors[type]} text-white p-4 rounded-xl shadow-lg transition-all duration-300 transform translate-x-full max-w-sm`;
    notification.innerHTML = `
        <div class="flex items-center gap-3">
            <i class="${icons[type]}"></i>
            <span class="flex-1">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (container.contains(notification)) {
                container.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Filter Functions
function applyFilters() {
    activeFilters.search = document.getElementById('search-input').value.toLowerCase();
    activeFilters.category = document.getElementById('category-filter').value;
    activeFilters.brand = document.getElementById('brand-filter').value;
    activeFilters.sort = document.getElementById('sort-filter').value;
    activeFilters.minPrice = parseInt(document.getElementById('min-price').value) || null;
    activeFilters.maxPrice = parseInt(document.getElementById('max-price').value) || null;
    
    console.log('Applying filters:', activeFilters);
    filterProducts();
}

function quickFilter(filterType) {
    console.log('Quick filter clicked:', filterType);
    
    // Toggle filter
    if (activeFilters.quickFilter === filterType) {
        activeFilters.quickFilter = null;
    } else {
        activeFilters.quickFilter = filterType;
    }
    
    // Update button states
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    const clickedBtn = event.target.closest('.quick-filter-btn');
    if (clickedBtn && activeFilters.quickFilter === filterType) {
        clickedBtn.classList.add('active');
    }
    
    filterProducts();
}

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
        element.classList.remove('bg-gradient-to-r', 'from-gray-200', 'to-gray-300', 'text-gray-700');
    });
    
    // Set first pills as active
    const firstCategoryPill = document.querySelector('.category-pill');
    const firstBrandPill = document.querySelector('.brand-pill');
    
    if (firstCategoryPill) {
        firstCategoryPill.classList.add('active');
        firstCategoryPill.classList.add('bg-gradient-to-r', 'from-gray-200', 'to-gray-300', 'text-gray-700');
    }
    if (firstBrandPill) {
        firstBrandPill.classList.add('active');
        firstBrandPill.classList.add('bg-gradient-to-r', 'from-gray-200', 'to-gray-300', 'text-gray-700');
    }
    
    console.log('Filters cleared, calling filterProducts');
    filterProducts();
}

function filterProducts() {
    console.log('filterProducts called with activeFilters:', activeFilters);
    console.log('Total products before filtering:', products.length);
    
    filteredProducts = products.filter(product => {
        // Search filter
        if (activeFilters.search && !product.name.toLowerCase().includes(activeFilters.search)) {
            return false;
        }
        
        // Category filter - use category_slug from API
        if (activeFilters.category && product.category_slug !== activeFilters.category) {
            return false;
        }
        
        // Brand filter - use brand_slug from API
        if (activeFilters.brand && product.brand_slug !== activeFilters.brand) {
            return false;
        }
        
        // Price range filter
        const productPrice = parseFloat(product.price);
        if (activeFilters.minPrice && productPrice < activeFilters.minPrice) {
            console.log(`Product ${product.name} filtered out: price ${productPrice} < min ${activeFilters.minPrice}`);
            return false;
        }
        if (activeFilters.maxPrice && productPrice > activeFilters.maxPrice) {
            console.log(`Product ${product.name} filtered out: price ${productPrice} > max ${activeFilters.maxPrice}`);
            return false;
        }
        
        // Quick filter - check product flags
        if (activeFilters.quickFilter) {
            if (activeFilters.quickFilter === 'bestseller' && !product.is_bestseller) return false;
            if (activeFilters.quickFilter === 'discount' && !product.has_discount) return false;
            if (activeFilters.quickFilter === 'new' && !product.is_new) return false;
            if (activeFilters.quickFilter === 'luxury' && !product.is_luxury) return false;
        }
        
        return true;
    });
    
    console.log('Filtered products count:', filteredProducts.length);
    
    // Sort products
    if (activeFilters.sort === 'price-low') {
        filteredProducts.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
    } else if (activeFilters.sort === 'price-high') {
        filteredProducts.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
    } else if (activeFilters.sort === 'rating') {
        filteredProducts.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    } else if (activeFilters.sort === 'name') {
        filteredProducts.sort((a, b) => a.name.localeCompare(b.name));
    } else if (activeFilters.sort === 'newest') {
        filteredProducts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (activeFilters.sort === 'bestseller') {
        filteredProducts.sort((a, b) => {
            if (a.is_bestseller && !b.is_bestseller) return -1;
            if (!a.is_bestseller && b.is_bestseller) return 1;
            return 0;
        });
    }
    
    // Reset pagination when filters are applied
    currentPageNumber = 1;
    hasMoreProducts = true;
    const endMessage = document.getElementById('end-message');
    if (endMessage) {
        endMessage.classList.add('hidden');
    }
    
    renderProducts(filteredProducts);
    updateResultsInfo();
    updateActiveFilters();
}

function updateResultsInfo() {
    const resultsCount = document.getElementById('results-count');
    const noResults = document.getElementById('no-results');
    const productsGrid = document.getElementById('products-grid');
    
    if (filteredProducts.length === 0) {
        resultsCount.textContent = 'هیچ محصولی یافت نشد';
        noResults.classList.remove('hidden');
        productsGrid.classList.add('hidden');
    } else {
        resultsCount.textContent = `نمایش ${toPersianNumber(filteredProducts.length)} محصول از ${toPersianNumber(products.length)}`;
        noResults.classList.add('hidden');
        productsGrid.classList.remove('hidden');
    }
}

function updateActiveFilters() {
    const activeFiltersContainer = document.getElementById('active-filters');
    activeFiltersContainer.innerHTML = '';
    
    if (activeFilters.search) {
        addFilterTag(`جستجو: ${activeFilters.search}`, () => {
            activeFilters.search = '';
            document.getElementById('search-input').value = '';
            filterProducts();
        });
    }
    
    if (activeFilters.category) {
        addFilterTag(`دسته: ${activeFilters.category}`, () => {
            activeFilters.category = '';
            document.getElementById('category-filter').value = '';
            filterProducts();
        });
    }
    
    if (activeFilters.brand) {
        addFilterTag(`برند: ${activeFilters.brand}`, () => {
            activeFilters.brand = '';
            document.getElementById('brand-filter').value = '';
            filterProducts();
        });
    }
    
    if (activeFilters.minPrice || activeFilters.maxPrice) {
        const priceText = `قیمت: ${activeFilters.minPrice ? toPersianNumber(activeFilters.minPrice.toLocaleString()) : '۰'} - ${activeFilters.maxPrice ? toPersianNumber(activeFilters.maxPrice.toLocaleString()) : '∞'}`;
        addFilterTag(priceText, () => {
            activeFilters.minPrice = null;
            activeFilters.maxPrice = null;
            document.getElementById('min-price').value = '';
            document.getElementById('max-price').value = '';
            filterProducts();
        });
    }
    
    if (activeFilters.quickFilter) {
        const filterNames = {
            bestseller: 'پرفروش',
            discount: 'تخفیف‌دار',
            new: 'جدید',
            luxury: 'لوکس'
        };
        addFilterTag(filterNames[activeFilters.quickFilter], () => {
            activeFilters.quickFilter = null;
            filterProducts();
        });
    }
}

function addFilterTag(text, onRemove) {
    const activeFiltersContainer = document.getElementById('active-filters');
    const tag = document.createElement('span');
    tag.className = 'bg-purple-100 text-purple-600 px-3 py-1 rounded-lg text-sm flex items-center gap-2';
    tag.innerHTML = `
        ${text}
        <button onclick="this.parentElement.remove(); (${onRemove.toString()})();" class="hover:text-purple-800">
            <i class="fas fa-times text-xs"></i>
        </button>
    `;
    activeFiltersContainer.appendChild(tag);
}

function toggleView(view) {
    console.log('Toggling view to:', view);
    currentView = view;
    
    const grid = document.getElementById('products-grid');
    const gridBtn = document.getElementById('grid-view');
    const listBtn = document.getElementById('list-view');
    
    if (!grid) {
        console.error('Products grid not found!');
        return;
    }
    
    // Update button states
    if (gridBtn && listBtn) {
    if (view === 'grid') {
            gridBtn.classList.add('bg-purple-600', 'text-white');
            gridBtn.classList.remove('bg-gray-200', 'text-gray-600');
            listBtn.classList.add('bg-gray-200', 'text-gray-600');
            listBtn.classList.remove('bg-purple-600', 'text-white');
    } else {
            listBtn.classList.add('bg-purple-600', 'text-white');
            listBtn.classList.remove('bg-gray-200', 'text-gray-600');
            gridBtn.classList.add('bg-gray-200', 'text-gray-600');
            gridBtn.classList.remove('bg-purple-600', 'text-white');
        }
    }
    
    // Re-render products with new view
    renderProducts(filteredProducts);
}

function toPersianNumber(num) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    // Add thousands separators first
    const formatted = num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    // Then convert to Persian digits
    return formatted.replace(/\d/g, (digit) => persianDigits[digit]);
}

// Hearts Background
function createHeart() {
    const heart = document.createElement('div');
    heart.className = 'heart';
    heart.innerHTML = '💖';
    
    // Random size
    const size = Math.random() * 30 + 20; // 20px to 50px
    heart.style.fontSize = size + 'px';
    
    // Random position
    heart.style.left = Math.random() * 100 + '%';
    heart.style.top = Math.random() * 100 + '%';
    
    return heart;
}

function createLantern() {
    const lantern = document.createElement('div');
    lantern.className = 'lantern';
    
    lantern.innerHTML = `
        <div class="lantern-body">
            <div class="lantern-handle"></div>
            <div class="lantern-top"></div>
            <div class="lantern-flame"></div>
            <div class="lantern-light"></div>
        </div>
    `;
    
    // Random position
    lantern.style.left = Math.random() * 100 + '%';
    
    // Random animation delay
    lantern.style.animationDelay = Math.random() * 12 + 's';
    
    return lantern;
}

function createStar() {
    const star = document.createElement('div');
    star.className = 'star';
    star.innerHTML = '✨';
    
    // Random size
    const size = Math.random() * 15 + 10; // 10px to 25px
    star.style.fontSize = size + 'px';
    
    // Random position
    star.style.left = Math.random() * 100 + '%';
    star.style.top = Math.random() * 100 + '%';
    
    // Random animation delay
    star.style.animationDelay = Math.random() * 3 + 's';
    
    return star;
}

function initHeartsBackground() {
    const heartsContainer = document.getElementById('hearts-bg');
    const heartCount = 25; // Number of hearts
    const starCount = 15; // Number of stars
    
    // Create hearts
    for (let i = 0; i < heartCount; i++) {
        const heart = createHeart();
        heartsContainer.appendChild(heart);
    }
    
    // Create stars for dark mode
    for (let i = 0; i < starCount; i++) {
        const star = createStar();
        heartsContainer.appendChild(star);
    }
    
    // Create lanterns for dark mode
    for (let i = 0; i < 4; i++) {
        const lantern = createLantern();
        heartsContainer.appendChild(lantern);
    }
}

// Continuously create new lanterns in dark mode
function startLanternAnimation() {
    setInterval(() => {
        if (document.body.classList.contains('dark')) {
            const heartsContainer = document.getElementById('hearts-bg');
            const lantern = createLantern();
            heartsContainer.appendChild(lantern);
            
            // Remove lantern after animation completes
            setTimeout(() => {
                if (heartsContainer.contains(lantern)) {
                    heartsContainer.removeChild(lantern);
                }
            }, 15000);
        }
    }, 4000); // Create new lantern every 4 seconds
}

// Product Modal Functions
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const modalContent = document.getElementById('modal-product-content');
    modalContent.innerHTML = `
        <div class="grid lg:grid-cols-2 gap-4 lg:gap-8">
            <!-- Product Image -->
            <div class="space-y-3 lg:space-y-4">
                <div id="main-product-image" class="w-full h-48 sm:h-64 lg:h-80 bg-gradient-to-br from-pink-200 to-purple-200 rounded-2xl flex items-center justify-center shadow-lg transition-all duration-300">
                    ${product.images && product.images.length > 0 
                        ? `<img src="${product.images[0].image}" alt="${product.name}" class="w-full h-full object-cover rounded-2xl">`
                        : `<i class="fas fa-image text-4xl sm:text-5xl lg:text-6xl text-gray-400"></i>`
                    }
                </div>
                
                <!-- Product Gallery Thumbnails -->
                <div class="flex gap-2 justify-center lg:justify-start">
                    ${product.images && product.images.length > 0 ? product.images.map((img, index) => `
                        <div onclick="changeMainImage('${img.image}', ${index})" class="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-pink-200 to-purple-200 rounded-lg flex items-center justify-center border-2 ${index === 0 ? 'border-purple-500' : 'border-transparent'} cursor-pointer">
                            <img src="${img.image}" alt="${product.name}" class="w-full h-full object-cover rounded-lg">
                    </div>
                    `).join('') : ''}
                </div>
            </div>
            
            <!-- Product Info -->
            <div class="space-y-4 lg:space-y-6">
                <div>
                    <h1 class="text-lg sm:text-xl lg:text-2xl font-bold mb-2 lg:mb-3 text-gray-900 dark:text-white">${product.name}</h1>
                    <p class="text-sm lg:text-base text-gray-900 dark:text-gray-400 mb-3 lg:mb-4">دسته‌بندی: ${product.category_name || 'دسته‌بندی'}</p>
                    
                    <!-- Rating -->
                    <div class="flex items-center gap-2 lg:gap-3 mb-3 lg:mb-4">
                        <div class="flex text-yellow-400">
                            ${Array(5).fill().map((_, i) => {
                                const rating = product.rating || 0;
                                const starIndex = i + 1;
                                if (starIndex <= Math.floor(rating)) {
                                    return '<i class="fas fa-star text-sm"></i>';
                                } else if (starIndex === Math.ceil(rating) && rating % 1 !== 0) {
                                    return '<i class="fas fa-star-half-alt text-sm"></i>';
                                } else {
                                    return '<i class="far fa-star text-sm"></i>';
                                }
                            }).join('')}
                        </div>
                        <span class="font-semibold text-sm lg:text-base text-gray-900 dark:text-white">${product.rating || 0}</span>
                        <span class="text-gray-900 dark:text-gray-400 text-sm">(${product.review_count || 0} نظر)</span>
                    </div>
                    
                    <!-- Price -->
                    <div class="flex flex-wrap items-center gap-2 lg:gap-3 mb-4 lg:mb-6">
                        <span class="text-lg lg:text-xl font-bold text-purple-600">${toPersianNumber(product.price)} تومان</span>
                        ${product.original_price ? `
                            <span class="text-gray-900 dark:text-gray-400 line-through text-sm">${toPersianNumber(product.original_price)} تومان</span>
                            <span class="bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 px-2 py-1 rounded-lg text-xs font-bold">${product.discount_percentage || 0}% تخفیف</span>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Product Options -->
                <div class="space-y-3 lg:space-y-4">
                    <div>
                        <h3 class="font-bold mb-2 text-sm lg:text-base text-gray-900 dark:text-white">رنگ:</h3>
                        <div class="flex gap-2">
                            <button class="w-8 h-8 lg:w-10 lg:h-10 bg-red-500 rounded-full border-2 border-purple-500 shadow-lg"></button>
                            <button class="w-8 h-8 lg:w-10 lg:h-10 bg-pink-500 rounded-full border-2 border-transparent hover:border-purple-500 shadow-lg transition-colors"></button>
                            <button class="w-8 h-8 lg:w-10 lg:h-10 bg-purple-500 rounded-full border-2 border-transparent hover:border-purple-500 shadow-lg transition-colors"></button>
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="font-bold mb-2 text-sm lg:text-base text-gray-900 dark:text-white">تعداد:</h3>
                        <div class="flex items-center gap-3">
                            <button onclick="updateModalQuantity(-1)" class="w-8 h-8 lg:w-10 lg:h-10 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg flex items-center justify-center font-bold transition-colors text-sm lg:text-base text-gray-900 dark:text-gray-300">-</button>
                            <span id="modal-quantity" class="text-base lg:text-lg font-bold w-6 lg:w-8 text-center text-gray-900 dark:text-white">1</span>
                            <button onclick="updateModalQuantity(1)" class="w-8 h-8 lg:w-10 lg:h-10 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg flex items-center justify-center font-bold transition-colors text-sm lg:text-base text-gray-900 dark:text-gray-300">+</button>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="space-y-2">
                    <button onclick="addToCartFromModal(${product.id})" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-2.5 lg:py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 text-sm lg:text-base">
                        <i class="fas fa-cart-plus"></i>
                        افزودن به سبد خرید
                    </button>
                    <button class="w-full bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 py-2.5 lg:py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 text-sm lg:text-base text-gray-900 dark:text-gray-300">
                        <i class="fas fa-heart"></i>
                        افزودن به علاقه‌مندی‌ها
                    </button>
                </div>
                
                <!-- Product Description -->
                <div class="bg-white dark:bg-gray-800 rounded-lg p-3 lg:p-4 border border-gray-200 dark:border-gray-700">
                    <h3 class="font-semibold mb-3 text-sm lg:text-base text-gray-900 dark:text-white">مشخصات محصول</h3>
                    
                    <!-- Product Details Grid -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                        <div class="flex items-center gap-2">
                            <i class="fas fa-tag text-purple-500 text-sm"></i>
                            <span class="text-xs lg:text-sm text-gray-700 dark:text-gray-300">دسته‌بندی:</span>
                            <span class="text-xs lg:text-sm font-medium text-gray-900 dark:text-white">${product.category_name || 'دسته‌بندی'}</span>
                        </div>
                        ${product.brand_name ? `
                        <div class="flex items-center gap-2">
                            <i class="fas fa-crown text-purple-500 text-sm"></i>
                            <span class="text-xs lg:text-sm text-gray-700 dark:text-gray-300">برند:</span>
                            <span class="text-xs lg:text-sm font-medium text-gray-900 dark:text-white">${product.brand_name}</span>
                        </div>
                        ` : ''}
                        <div class="flex items-center gap-2">
                            <i class="fas fa-star text-yellow-500 text-sm"></i>
                            <span class="text-xs lg:text-sm text-gray-700 dark:text-gray-300">امتیاز:</span>
                            <span class="text-xs lg:text-sm font-medium text-gray-900 dark:text-white">${product.rating || 0}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <i class="fas fa-comments text-blue-500 text-sm"></i>
                            <span class="text-xs lg:text-sm text-gray-700 dark:text-gray-300">نظرات:</span>
                            <span class="text-xs lg:text-sm font-medium text-gray-900 dark:text-white">${product.review_count || 0}</span>
                        </div>
                    </div>
                    
                    <!-- Product Description -->
                    ${product.description ? `
                    <div class="mb-4">
                        <h4 class="font-medium mb-2 text-sm lg:text-base text-gray-900 dark:text-white">توضیحات:</h4>
                        <p class="text-xs lg:text-sm text-gray-700 dark:text-gray-300 leading-relaxed">${product.description}</p>
                    </div>
                    ` : ''}
                    
                    ${product.short_description ? `
                    <div class="mb-4">
                        <h4 class="font-medium mb-2 text-sm lg:text-base text-gray-900 dark:text-white">خلاصه:</h4>
                        <p class="text-xs lg:text-sm text-gray-700 dark:text-gray-300 leading-relaxed">${product.short_description}</p>
                    </div>
                    ` : ''}
                    
                    <!-- Product Features -->
                    <div class="border-t border-gray-200 dark:border-gray-700 pt-3">
                        <h4 class="font-medium mb-2 text-sm lg:text-base text-gray-900 dark:text-white">ویژگی‌ها:</h4>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs lg:text-sm">
                            <div class="flex items-center gap-2">
                            <i class="fas fa-check-circle text-green-500 text-xs"></i>
                                <span class="text-gray-700 dark:text-gray-300">کیفیت تضمینی</span>
                        </div>
                            <div class="flex items-center gap-2">
                            <i class="fas fa-check-circle text-green-500 text-xs"></i>
                                <span class="text-gray-700 dark:text-gray-300">ارسال سریع</span>
                        </div>
                            <div class="flex items-center gap-2">
                            <i class="fas fa-check-circle text-green-500 text-xs"></i>
                                <span class="text-gray-700 dark:text-gray-300">ضمانت بازگشت</span>
                        </div>
                            <div class="flex items-center gap-2">
                            <i class="fas fa-check-circle text-green-500 text-xs"></i>
                                <span class="text-gray-700 dark:text-gray-300">پشتیبانی ۲۴/۷</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('product-modal').classList.add('active');
}

function closeProductModal() {
    document.getElementById('product-modal').classList.remove('active');
}

let modalQuantity = 1;

function updateModalQuantity(change) {
    modalQuantity = Math.max(1, modalQuantity + change);
    document.getElementById('modal-quantity').textContent = modalQuantity;
}

function addToCartFromModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += modalQuantity;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: modalQuantity,
            image: product.image,
            color: product.color,
            iconColor: product.iconColor
        });
    }
    
    updateCartCount();
    renderCart();
    closeProductModal();
    showNotification(`${modalQuantity} عدد ${product.name} به سبد خرید اضافه شد!`);
    modalQuantity = 1; // Reset quantity
}

// Change main product image in modal
function changeMainImage(imageSrc, index) {
    const mainImage = document.getElementById('main-product-image');
    
    if (mainImage) {
        mainImage.innerHTML = `<img src="${imageSrc}" alt="Product" class="w-full h-full object-cover rounded-2xl">`;
        
        // Update thumbnail borders
        const thumbnails = mainImage.parentElement.querySelectorAll('.flex.gap-2 > div');
        thumbnails.forEach((thumb, i) => {
            const border = thumb.querySelector('.border-2');
            if (border) {
                border.className = `border-2 ${i === index ? 'border-purple-500' : 'border-transparent'}`;
            }
        });
    }
}

// Blog Modal Functions
function openBlogModal(blogId) {
    const blog = blogs.find(b => b.id === blogId);
    if (!blog) return;
    
    const modalContent = document.getElementById('modal-product-content');
    modalContent.innerHTML = `
        <div class="max-w-4xl mx-auto">
            <!-- Blog Header -->
            <div class="h-32 sm:h-40 lg:h-48 bg-gradient-to-br ${blog.color} rounded-2xl flex items-center justify-center mb-4 lg:mb-6">
                <i class="${blog.image} text-4xl sm:text-5xl lg:text-6xl ${blog.iconColor}"></i>
            </div>
            
            <!-- Blog Content -->
            <div class="space-y-4 lg:space-y-6 text-sm lg:text-base">
                ${blog.content}
                
                <!-- Share Buttons -->
                <div class="pt-4 lg:pt-6 border-t theme-border">
                    <h4 class="font-bold mb-3 lg:mb-4 text-sm lg:text-base">اشتراک‌گذاری:</h4>
                    <div class="flex flex-wrap gap-2 lg:gap-3">
                        <button class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 lg:px-4 py-2 rounded-lg transition-colors text-xs lg:text-sm">
                            <i class="fab fa-telegram"></i>
                            تلگرام
                        </button>
                        <button class="flex items-center gap-2 bg-pink-600 hover:bg-pink-700 text-white px-3 lg:px-4 py-2 rounded-lg transition-colors text-xs lg:text-sm">
                            <i class="fab fa-instagram"></i>
                            اینستاگرام
                        </button>
                        <button class="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 lg:px-4 py-2 rounded-lg transition-colors text-xs lg:text-sm">
                            <i class="fab fa-whatsapp"></i>
                            واتساپ
                        </button>
                    </div>
                </div>
                
                <!-- Related Posts -->
                <div class="pt-4 lg:pt-6 border-t theme-border">
                    <h4 class="font-bold mb-3 lg:mb-4 text-sm lg:text-base">مطالب مرتبط:</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 lg:gap-4">
                        ${blogs.filter(b => b.id !== blogId).slice(0, 2).map(relatedBlog => `
                            <div onclick="openBlogModal(${relatedBlog.id})" class="flex gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors">
                                <div class="w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br ${relatedBlog.color} rounded-xl flex items-center justify-center flex-shrink-0">
                                    <i class="${relatedBlog.image} text-sm lg:text-lg ${relatedBlog.iconColor}"></i>
                                </div>
                                <div>
                                    <h5 class="font-bold text-xs lg:text-sm mb-1 line-clamp-2">${relatedBlog.title}</h5>
                                    <p class="text-xs theme-text-secondary">${relatedBlog.date}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('product-modal').classList.add('active');
}

// Compact Filter Functions
let isCompactOpen = false;

function toggleCompact() {
    const filterPanel = document.getElementById('filter-panel');
    
    if (!isCompactOpen) {
        // Open compact
        filterPanel.style.transform = 'translateX(0)';
        isCompactOpen = true;
    } else {
        // Close compact
        filterPanel.style.transform = 'translateX(100%)';
        isCompactOpen = false;
    }
}

function setCategoryFilter(category) {
    // Update active state
    document.querySelectorAll('.category-pill').forEach(pill => {
        pill.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Set filter
    activeFilters.category = category;
    filterProducts();
}

// ===== CORE APP JAVASCRIPT FUNCTIONS =====

// Auth tab switching
function showTab(tabName) {
    // Hide all forms
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.add('hidden');
    });
    
    // Show selected form
    if (tabName === 'login') {
        document.getElementById('loginForm').classList.remove('hidden');
    } else if (tabName === 'register') {
        document.getElementById('registerForm').classList.remove('hidden');
    }
    
    // Update tab buttons
    document.querySelectorAll('#authTabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Show forgot password form
function showForgotPassword() {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.add('hidden');
    });
    document.getElementById('forgotForm').classList.remove('hidden');
}

// Password strength checker
function checkPasswordStrength(password, elementId = 'passwordStrength') {
    const strengthElement = document.getElementById(elementId);
    if (!strengthElement) return;
    
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    strengthElement.className = 'password-strength';
    
    if (strength <= 1) {
        strengthElement.classList.add('strength-weak');
    } else if (strength <= 2) {
        strengthElement.classList.add('strength-medium');
    } else {
        strengthElement.classList.add('strength-strong');
    }
}

// Profile tab switching
function showProfileTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.remove('hidden');
    
    // Update tab buttons
    document.querySelectorAll('#profileTabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Load cities based on selected province using AJAX
function loadCities(preserveCurrentCity = false) {
    const provinceSelect = document.getElementById('provinceSelect');
    const citySelect = document.getElementById('citySelect');
    if (!provinceSelect || !citySelect) return;
    
    const selectedProvince = provinceSelect.value;
    
    // Store current city selection if preserving
    let currentCityId = null;
    if (preserveCurrentCity) {
        currentCityId = citySelect.value;
    }
    
    citySelect.innerHTML = '<option value="">انتخاب شهر</option>';
    
    if (selectedProvince) {
        // Show loading state
        citySelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
        
        // Make AJAX request to get cities
        fetch(`/accounts/get-cities/?province_id=${selectedProvince}`)
            .then(response => response.json())
            .then(data => {
                citySelect.innerHTML = '<option value="">انتخاب شهر</option>';
                
                if (data.cities && data.cities.length > 0) {
                    data.cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.id;
                        option.textContent = city.name;
                        
                        // Select the current city if preserving and it matches
                        if (preserveCurrentCity && currentCityId && city.id == currentCityId) {
                            option.selected = true;
                        }
                        
                        citySelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                citySelect.innerHTML = '<option value="">خطا در بارگذاری شهرها</option>';
            });
    }
}

// Preview image function
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const avatar = document.querySelector('.profile-avatar');
            if (avatar) {
                avatar.innerHTML = `<img src="${e.target.result}" alt="پروفایل" class="w-full h-full rounded-full object-cover">
                    <div class="edit-icon">
                        <i class="fas fa-camera"></i>
                    </div>`;
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Show verification step for forgot password
function showVerificationStep() {
    const phoneStep = document.getElementById('phoneStep');
    const verificationStep = document.getElementById('verificationStep');
    if (phoneStep && verificationStep) {
        phoneStep.classList.add('hidden');
        verificationStep.classList.remove('hidden');
    }
}

// Show phone step for forgot password
function showPhoneStep() {
    const phoneStep = document.getElementById('phoneStep');
    const verificationStep = document.getElementById('verificationStep');
    if (phoneStep && verificationStep) {
        phoneStep.classList.remove('hidden');
        verificationStep.classList.add('hidden');
    }
}

// Go back to phone step
function goBackToPhoneStep() {
    showPhoneStep();
    // Clear any error messages
    const messages = document.querySelectorAll('.bg-red-100, .bg-yellow-100, .bg-green-100');
    messages.forEach(msg => msg.remove());
}

// Form handlers
function handleLogin(event) {
    // Form will be submitted normally
    return true;
}

function handleRegister(event) {
    const passwords = event.target.querySelectorAll('input[type="password"]');
    
    if (passwords[0].value !== passwords[1].value) {
        alert('رمزهای عبور مطابقت ندارند!');
        event.preventDefault();
        return false;
    }
    
    return true;
}

function changePassword(event) {
    event.preventDefault();
    const passwords = event.target.querySelectorAll('input[type="password"]');
    
    if (passwords[1].value !== passwords[2].value) {
        alert('رمزهای عبور جدید مطابقت ندارند!');
        return false;
    }
    
    alert('رمز عبور با موفقیت تغییر کرد! 🔐');
    event.target.reset();
    return false;
}

// ===== END CORE APP JAVASCRIPT FUNCTIONS =====

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Start countdown timer - شروع تایمر تخفیف
    startCountdown();
    
    // Initialize hearts background
    initHeartsBackground();
    
    // Start lantern animation
    startLanternAnimation();
    
    // Load products from API
    loadProducts();
    
    // Load theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
        document.getElementById('theme-icon').className = 'fas fa-sun text-lg';
    }
    
    // Check if we're on the products page based on URL
    if (window.location.pathname.includes('/shop/products/') || window.location.hash === '#products') {
        console.log('Detected products page from URL, setting currentPage to products');
        currentPage = 'products';
    }
    
    // Initialize cart
    updateCartCount();
    renderCart();
    
    // Add search event listener
    const searchInputEl = document.getElementById('search-input');
    if (searchInputEl) {
        searchInputEl.addEventListener('input', function() {
            activeFilters.search = this.value.toLowerCase();
            filterProducts();
        });
    }
    
    // Add filter event listeners
    const categoryFilter = document.getElementById('category-filter');
    const brandFilter = document.getElementById('brand-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            activeFilters.category = this.value;
            filterProducts();
        });
    }
    
    if (brandFilter) {
        brandFilter.addEventListener('change', function() {
            activeFilters.brand = this.value;
            filterProducts();
        });
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            activeFilters.sort = this.value;
            filterProducts();
        });
    }
    
    // Load products only once when page loads
    if (window.location.pathname.includes('/shop/products/')) {
        console.log('On products page, loading products once');
        
        // Check if products are already loaded
        if (products.length === 0) {
            console.log('No products loaded, loading initial products');
            loadProducts(1, false);
        } else {
            console.log('Products already loaded, rendering existing products');
            renderProducts(filteredProducts);
            updateResultsInfo();
        }
    }
    
    // Add event listeners for price range
    document.addEventListener('DOMContentLoaded', function() {
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
        
        // View toggle buttons
        const gridViewBtn = document.getElementById('grid-view');
        const listViewBtn = document.getElementById('list-view');
        
        if (gridViewBtn) {
            gridViewBtn.addEventListener('click', function() {
                toggleView('grid');
            });
        }
        
        if (listViewBtn) {
            listViewBtn.addEventListener('click', function() {
                toggleView('list');
            });
        }
    });
});

// Load more products function
function loadMoreProducts() {
    console.log('Load more products clicked, current page:', currentPageNumber);
    
    if (!hasMoreProducts) {
        console.log('No more products to load');
        return;
    }
    
    // Show loading indicator
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (loadMoreBtn) {
        loadMoreBtn.classList.add('hidden');
    }
    
    if (loadingIndicator) {
        loadingIndicator.classList.remove('hidden');
    }
    
    // Load next page
    const nextPage = currentPageNumber + 1;
    console.log('Loading next page:', nextPage);
    
    loadProducts(nextPage, true).then(() => {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
        }
        
        // Show load more button if there are more products
        if (hasMoreProducts && loadMoreBtn) {
            loadMoreBtn.classList.remove('hidden');
        }
        
        console.log('Load more completed, total products:', products.length);
    }).catch(error => {
        console.error('Error loading more products:', error);
        
        // Show load more button again on error
        if (loadMoreBtn) {
            loadMoreBtn.classList.remove('hidden');
        }
        
        if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
        }
    });
}

function applyPriceFilters() {
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    
    // Convert formatted prices to numbers
    const minPriceNum = minPrice ? parseInt(minPrice.replace(/,/g, '')) : null;
    const maxPriceNum = maxPrice ? parseInt(maxPrice.replace(/,/g, '')) : null;
    
    console.log('Applying price filters:', { minPrice: minPriceNum, maxPrice: maxPriceNum });
    
    // Update activeFilters
    activeFilters.minPrice = minPriceNum;
    activeFilters.maxPrice = maxPriceNum;
    
    filterProducts();
}

function renderGridView(productsToRender, grid) {
    productsToRender.forEach(product => {
        const productCard = `
            <a href="/shop/product/${product.slug}/" class="product-card" style="text-decoration: none; color: inherit;">
                <!-- Badges -->
                ${product.has_discount ? `
                    <div class="discount-badge">
                        <i class="fas fa-fire mr-1"></i>
                        ${product.discount_percentage || 0}% تخفیف
                    </div>
                ` : ''}
                ${product.is_bestseller ? `
                    <div class="bestseller-badge">
                        <i class="fas fa-star mr-1"></i>
                        پرفروش
                    </div>
                ` : ''}
                ${product.is_new && !product.is_bestseller ? `
                    <div class="new-badge">
                        <i class="fas fa-star mr-1"></i>
                        جدید
                    </div>
                ` : ''}
                <!-- Image Container -->
                <div class="product-image-container">
                    ${product.images && product.images.length > 0 
                        ? `<img src="${product.images[0].image}" alt="${product.name}" class="product-image">`
                        : `<div class="placeholder-container">
                            <div class="placeholder-icon">
                                <i class="fas fa-image"></i>
                            </div>
                            <div class="placeholder-text">بدون تصویر</div>
                           </div>`
                    }
                    <!-- Overlay with Title and Category -->
                    <div class="product-overlay">
                        <div class="category-tag">
                            <i class="fas fa-tag mr-1"></i>
                            ${product.category_name || 'دسته‌بندی'}
                        </div>
                        <div class="product-title">
                            ${product.name}
                        </div>
                    </div>
                </div>
                <div class="product-content">
                    <div class="product-info">
                        <div class="product-rating">
                            <div class="stars">
                                ${(() => {
                                    let stars = '';
                                    for (let i = 1; i <= 5; i++) {
                                        stars += i <= Math.round(product.rating) ? '<i class="fas fa-star"></i>' : '<i class="far fa-star"></i>';
                                    }
                                    return stars;
                                })()}
                            </div>
                            <span class="rating-text">(${product.rating || 0})</span>
                        </div>
                        <div class="product-price">
                            <span class="current-price">${product.price.toLocaleString()} تومان</span>
                            ${product.original_price ? `<span class="original-price">${product.original_price.toLocaleString()} تومان</span>` : ''}
                        </div>
                    </div>
                </div>
            </a>
        `;
        grid.innerHTML += productCard;
    });
}

function renderListView(productsToRender, grid) {
    productsToRender.forEach(product => {
        const productCard = `
            <a href="/shop/product/${product.slug}/" class="theme-card rounded-2xl shadow-lg overflow-hidden card-hover cursor-pointer flex" style="text-decoration: none; color: inherit;">
                <div class="w-32 h-32 bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center flex-shrink-0">
                    ${product.images && product.images.length > 0 
                        ? `<img src="${product.images[0].image}" alt="${product.name}" class="w-full h-full object-cover">`
                        : `<i class="fas fa-image text-3xl text-gray-400"></i>`
                    }
                </div>
                <div class="p-6 flex-1 flex items-center justify-between">
                    <div class="flex-1">
                        <div class="flex items-start justify-between mb-3">
                            <div>
                                <h3 class="text-lg font-bold mb-1">${product.name}</h3>
                                <div class="flex items-center gap-4 text-sm text-gray-600">
                                    <span class="flex items-center gap-1">
                                        <i class="fas fa-tag text-purple-500"></i>
                                        ${product.category_name || 'دسته‌بندی'}
                                    </span>
                                    ${product.brand_name ? `
                                    <span class="flex items-center gap-1">
                                        <i class="fas fa-crown text-blue-500"></i>
                                        ${product.brand_name}
                                    </span>
                                    ` : ''}
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="flex text-yellow-400">
                                    ${(() => {
                                        let stars = '';
                                        for (let i = 1; i <= 5; i++) {
                                            stars += i <= Math.round(product.rating) ? '<i class="fas fa-star"></i>' : '<i class="far fa-star"></i>';
                                        }
                                        return stars;
                                    })()}
                                </div>
                                <span class="rating-text">(${product.rating || 0})</span>
                            </div>
                        </div>
                        <div class="product-price">
                            <span class="current-price">${product.price.toLocaleString()} تومان</span>
                            ${product.original_price ? `<span class="original-price">${product.original_price.toLocaleString()} تومان</span>` : ''}
                        </div>
                    </div>
                </div>
            </a>
        `;
        grid.innerHTML += productCard;
    });
}
}