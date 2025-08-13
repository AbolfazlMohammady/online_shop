// Brand Products Page JavaScript Functions

function toggleView(view) {
    const gridView = document.getElementById('grid-view');
    const listView = document.getElementById('list-view');
    const productsGrid = document.getElementById('products-grid');
    
    if (view === 'grid') {
        gridView.classList.add('bg-purple-600', 'text-white');
        gridView.classList.remove('bg-gray-200', 'text-gray-600');
        listView.classList.add('bg-gray-200', 'text-gray-600');
        listView.classList.remove('bg-purple-600', 'text-white');
        productsGrid.classList.remove('grid-cols-1');
        productsGrid.classList.add('grid-cols-2', 'sm:grid-cols-3', 'lg:grid-cols-4');
    } else {
        listView.classList.add('bg-purple-600', 'text-white');
        listView.classList.remove('bg-gray-200', 'text-gray-600');
        gridView.classList.add('bg-gray-200', 'text-gray-600');
        gridView.classList.remove('bg-purple-600', 'text-white');
        productsGrid.classList.remove('grid-cols-2', 'sm:grid-cols-3', 'lg:grid-cols-4');
        productsGrid.classList.add('grid-cols-1');
    }
}

function openProductModal(productId) {
    window.location.href = `/shop/product/${productId}/`;
}

function addToCart(productId) {
    // Find the product card to get product information
    const productCard = document.querySelector(`[data-product-id="${productId}"]`) || 
                       document.querySelector(`.product-card:has(button[onclick*="${productId}"])`);
    
    if (!productCard) {
        console.error('Product card not found for ID:', productId);
        return;
    }
    
    // Extract product information from the card
    const name = productCard.querySelector('h3, h4, .product-title')?.textContent?.trim() || 'محصول';
    const priceText = (productCard.querySelector('.text-purple-600, .current-price')?.textContent || '').replace(/[^\d]/g, '') || '0';
    const price = parseInt(priceText) || 0;
    const imgEl = productCard.querySelector('img');
    const image = imgEl ? imgEl.getAttribute('src') : null;
    
    // Add to cart
    try {
        const raw = localStorage.getItem('cart') || '[]';
        const cart = JSON.parse(raw);
        const existing = cart.find(item => item.id === productId);
        
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
            showNotification(`تعداد ${name} به ${existing.quantity} عدد افزایش یافت!`);
        } else {
            cart.push({
                id: productId,
                name: name,
                price: price,
                quantity: 1,
                image: image,
                color: 'from-pink-200 to-purple-200',
                iconColor: 'text-gray-400'
            });
            showNotification(`${name} به سبد خرید اضافه شد!`);
        }
        
        localStorage.setItem('cart', JSON.stringify(cart));
        
        // Update cart count
        const countEl = document.getElementById('cart-count');
        if (countEl) {
            const count = cart.reduce((total, item) => total + item.quantity, 0);
            countEl.textContent = count;
            countEl.classList.add('animate-pulse');
            setTimeout(() => countEl.classList.remove('animate-pulse'), 600);
        }
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('خطا در افزودن به سبد خرید', 'error');
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    const bg = type === 'success' ? 'bg-green-500' : 'bg-red-500';
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transition-all duration-300 transform translate-x-full ${bg}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.remove('translate-x-full'), 50);
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 2500);
}
