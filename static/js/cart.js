// Cart Page JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
  let cart = JSON.parse(localStorage.getItem('cart') || '[]');
  const shippingSettings = {
    shippingCost: 70000,
    freeShippingThreshold: 500000
  };

  // Initialize cart
  renderCartItems();
  updateCartSummary();
  updateCartCount();

  function renderCartItems() {
    const cartContainer = document.getElementById('cart-items');
    if (!cartContainer) return;

    if (cart.length === 0) {
      cartContainer.innerHTML = `
        <div class="text-center py-12">
          <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-shopping-cart text-2xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">سبد خرید شما خالی است</h3>
          <p class="text-gray-500 text-sm mb-4">محصولات مورد نظر خود را به سبد خرید اضافه کنید</p>
          <a href="/shop/products/" class="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            <i class="fas fa-shopping-bag"></i>
            مشاهده محصولات
          </a>
        </div>
      `;
      return;
    }

    cartContainer.innerHTML = cart.map(item => `
      <div class="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-md border border-gray-200 dark:border-gray-700">
        <!-- Product Image -->
        <div class="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-pink-200 to-purple-200 rounded-lg sm:rounded-xl flex items-center justify-center flex-shrink-0">
          ${item.image ? 
            `<img src="${item.image}" alt="${item.name}" class="w-full h-full object-cover rounded-lg sm:rounded-xl">` :
            `<i class="fas fa-image text-2xl text-gray-400"></i>`
          }
        </div>
        
        <!-- Product Info -->
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-gray-900 dark:text-white text-sm sm:text-base mb-1 truncate">${item.name}</h4>
          <p class="text-purple-600 dark:text-purple-400 font-bold text-sm sm:text-base">${item.price.toLocaleString()} تومان</p>
        </div>
        
        <!-- Quantity Controls -->
        <div class="flex items-center gap-2">
          <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})" class="w-8 h-8 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg flex items-center justify-center text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
            <i class="fas fa-minus text-xs"></i>
          </button>
          <span class="w-12 text-center font-semibold text-gray-900 dark:text-white text-sm sm:text-base">${item.quantity}</span>
          <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})" class="w-8 h-8 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg flex items-center justify-center text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
            <i class="fas fa-plus text-xs"></i>
          </button>
        </div>
        
        <!-- Remove Button -->
        <button onclick="removeFromCart(${item.id})" class="w-8 h-8 bg-red-100 hover:bg-red-200 dark:bg-red-900/20 dark:hover:bg-red-900/40 rounded-lg flex items-center justify-center text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors">
          <i class="fas fa-trash text-xs"></i>
        </button>
      </div>
    `).join('');
  }

  function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const countElement = document.getElementById('cart-count');
    if (countElement) {
      countElement.textContent = count;
    }
  }

  function updateCartSummary() {
    console.log('Updating cart summary, cart:', cart);
    const subtotal = cart.reduce((total, item) => {
      // Convert price to number and handle both string and number types
      const itemPrice = typeof item.price === 'string' ? parseFloat(item.price.replace(/[^\d.]/g, '')) : parseFloat(item.price) || 0;
      const itemQuantity = parseInt(item.quantity) || 0;
      const itemTotal = itemPrice * itemQuantity;
      console.log(`Item: ${item.name}, Price: ${itemPrice}, Quantity: ${itemQuantity}, Total: ${itemTotal}`);
      return total + itemTotal;
    }, 0);
    console.log('Subtotal calculated:', subtotal);
    
    const shipping = subtotal >= shippingSettings.freeShippingThreshold ? 0 : shippingSettings.shippingCost;
    const total = subtotal + shipping;
    
    console.log('Final calculations - Subtotal:', subtotal, 'Shipping:', shipping, 'Total:', total);
    
    const subtotalEl = document.getElementById('subtotal');
    const shippingEl = document.getElementById('shipping');
    const totalEl = document.getElementById('total');
    
    if (subtotalEl) subtotalEl.textContent = subtotal.toLocaleString() + ' تومان';
    if (shippingEl) shippingEl.textContent = shipping === 0 ? 'رایگان' : shipping.toLocaleString() + ' تومان';
    if (totalEl) totalEl.textContent = total.toLocaleString() + ' تومان';
  }

  // Global functions for cart operations
  window.removeFromCart = function(productId) {
    console.log('Removing product with ID:', productId);
    // Remove item from cart
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Update cart count in navbar
    updateCartCount();
    
    // Re-render cart
    renderCartItems();
    updateCartSummary();
  };

  window.updateQuantity = function(productId, newQuantity) {
    if (newQuantity <= 0) {
      window.removeFromCart(productId);
      return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
      item.quantity = newQuantity;
      localStorage.setItem('cart', JSON.stringify(cart));
      
      // Update cart count in navbar
      updateCartCount();
      
      // Re-render cart
      renderCartItems();
      updateCartSummary();
    }
  };

  window.checkout = function() {
    if (cart.length === 0) {
      alert('سبد خرید شما خالی است!');
      return;
    }
    // Redirect to checkout page
    window.location.href = '/shop/checkout/';
  };

  // Clear Cart function
  window.clearCart = function() {
    console.log('Clearing cart...');
    cart = [];
    localStorage.removeItem('cart');
    updateCartCount();
    renderCartItems();
    updateCartSummary();
    console.log('Cart cleared. Current cart:', cart);
  };
});
