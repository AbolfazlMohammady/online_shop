

// Global filter state
let activeFilters = {
    search: '',
    category: '',
    brand: '',
    sort: 'default',
    minPrice: null,
    maxPrice: null,
    quickFilter: null
};

// Main function to apply all filters and render products
function applyAllFilters() {
    // Corrected ID: product-list -> products-grid
    const productsGridContainer = document.getElementById('products-grid');
    if (!productsGridContainer) {
        console.error('Products grid container not found.');
        return;
    }

    productsGridContainer.innerHTML = ''; // Clear existing products
    let filteredProducts = [...products];

    // Apply all filters
    if (activeFilters.search) {
        const searchTerm = activeFilters.search.toLowerCase();
        filteredProducts = filteredProducts.filter(product =>
            product.name.toLowerCase().includes(searchTerm)
        );
    }
    if (activeFilters.category) {
        filteredProducts = filteredProducts.filter(product =>
            product.category === activeFilters.category
        );
    }
    if (activeFilters.brand) {
        filteredProducts = filteredProducts.filter(product =>
            product.brand === activeFilters.brand
        );
    }

    // Apply price range filter
    if (activeFilters.minPrice !== null && !isNaN(activeFilters.minPrice)) {
        filteredProducts = filteredProducts.filter(product =>
            product.price >= activeFilters.minPrice
        );
    }
    if (activeFilters.maxPrice !== null && !isNaN(activeFilters.maxPrice)) {
        filteredProducts = filteredProducts.filter(product =>
            product.price <= activeFilters.maxPrice
        );
    }
    
    // Apply sorting (you may need to adjust your sort values to match these)
    if (activeFilters.sort === 'price-low') {
        filteredProducts.sort((a, b) => a.price - b.price);
    } else if (activeFilters.sort === 'price-high') {
        filteredProducts.sort((a, b) => b.price - a.price);
    }

    // Render filtered products
    if (filteredProducts.length > 0) {
        filteredProducts.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <h3>${product.name}</h3>
                <p>قیمت: ${product.price.toLocaleString('fa-IR')} تومان</p>
                <p>دسته: ${product.category}</p>
                <p>برند: ${product.brand}</p>
            `;
            productsGridContainer.appendChild(productCard);
        });
        document.getElementById('no-results').classList.add('hidden');
    } else {
        productsGridContainer.innerHTML = ''; // Ensure container is empty
        document.getElementById('no-results').classList.remove('hidden');
    }

    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.textContent = `نمایش ${filteredProducts.length} محصول`;
    }
}

// Function to update the URL with current filters
function updateUrl() {
    const url = new URL(window.location.href);
    url.searchParams.set('search', activeFilters.search);
    url.searchParams.set('category', activeFilters.category);
    url.searchParams.set('brand', activeFilters.brand);
    url.searchParams.set('sort', activeFilters.sort);
    if (activeFilters.minPrice !== null) {
        url.searchParams.set('min_price', activeFilters.minPrice);
    } else {
        url.searchParams.delete('min_price');
    }
    if (activeFilters.maxPrice !== null) {
        url.searchParams.set('max_price', activeFilters.maxPrice);
    } else {
        url.searchParams.delete('max_price');
    }
    window.history.replaceState({}, '', url);
}

// Function to read filters from the URL
function readFiltersFromUrl() {
    const url = new URL(window.location.href);
    activeFilters.search = url.searchParams.get('search') || '';
    activeFilters.category = url.searchParams.get('category') || '';
    activeFilters.brand = url.searchParams.get('brand') || '';
    activeFilters.sort = url.searchParams.get('sort') || 'default';
    const minPrice = url.searchParams.get('min_price');
    const maxPrice = url.searchParams.get('max_price');
    
    activeFilters.minPrice = minPrice ? parseInt(minPrice) : null;
    activeFilters.maxPrice = maxPrice ? parseInt(maxPrice) : null;
    
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    if (minPriceInput && activeFilters.minPrice !== null) {
        minPriceInput.value = activeFilters.minPrice.toLocaleString('fa-IR');
    }
    if (maxPriceInput && activeFilters.maxPrice !== null) {
        maxPriceInput.value = activeFilters.maxPrice.toLocaleString('fa-IR');
    }
}

// Other functions
function toggleCompact() {
    const panel = document.getElementById('filter-panel');
    panel.classList.toggle('translate-x-full');
}

function clearFilters() {
    activeFilters = {
        search: '',
        category: '',
        brand: '',
        sort: 'default',
        minPrice: null,
        maxPrice: null,
        quickFilter: null
    };

    // Reset input fields
    const searchInput = document.getElementById('search-input');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const sortFilter = document.getElementById('sort-filter');
    
    if (searchInput) searchInput.value = '';
    if (minPriceInput) minPriceInput.value = '';
    if (maxPriceInput) maxPriceInput.value = '';
    if (sortFilter) sortFilter.value = 'default';

    // Reset active pill states
    document.querySelectorAll('.category-pill, .brand-pill, .quick-filter-btn').forEach(element => {
        element.classList.remove('active');
    });
    const allCategoryPill = document.querySelector('.category-pill[onclick="setCategoryFilter(\'\')"]');
    const allBrandPill = document.querySelector('.brand-pill[onclick="setBrandFilter(\'\')"]');
    if (allCategoryPill) allCategoryPill.classList.add('active');
    if (allBrandPill) allBrandPill.classList.add('active');

    updateUrl();
    applyAllFilters();
}

function formatPriceInput(input) {
    let value = input.value.replace(/[^\d]/g, '');
    if (value) {
        value = parseInt(value).toLocaleString('fa-IR');
    }
    input.value = value;
}

function setCategoryFilter(category) {
    activeFilters.category = category;
    updateUrl();
    applyAllFilters();
}

function setBrandFilter(brand) {
    activeFilters.brand = brand;
    updateUrl();
    applyAllFilters();
}

function quickFilter(type) {
    activeFilters.quickFilter = type;
    updateUrl();
    applyAllFilters();
}

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            activeFilters.search = this.value;
            updateUrl();
            applyAllFilters();
        });
    }
}

function initializePriceInputs() {
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    
    if (minPriceInput) {
        minPriceInput.addEventListener('input', function() {
            formatPriceInput(this);
            const cleanValue = this.value.replace(/[^\d]/g, '');
            activeFilters.minPrice = cleanValue ? parseInt(cleanValue) : null;
            updateUrl();
            applyAllFilters();
        });
    }
    
    if (maxPriceInput) {
        maxPriceInput.addEventListener('input', function() {
            formatPriceInput(this);
            const cleanValue = this.value.replace(/[^\d]/g, '');
            activeFilters.maxPrice = cleanValue ? parseInt(cleanValue) : null;
            updateUrl();
            applyAllFilters();
        });
    }
}

function initializeFilterPills() {
    document.querySelectorAll('.category-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            setCategoryFilter(category);
        });
    });
    
    document.querySelectorAll('.brand-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            const brand = this.getAttribute('data-brand');
            setBrandFilter(brand);
        });
    });
    
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filterType = this.getAttribute('data-quick-filter');
            quickFilter(filterType);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    readFiltersFromUrl();
    initializeSearch();
    initializePriceInputs();
    initializeFilterPills();
    
    const clearButton = document.getElementById('clear-filters-btn');
    if (clearButton) {
        clearButton.addEventListener('click', clearFilters);
    }
    
    // Initial load of products with URL filters applied
    applyAllFilters();
});