// Checkout Page JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
  // Load cart from localStorage
  const cart = JSON.parse(localStorage.getItem('cart') || '[]');
  
  // Shipping settings
  let shippingSettings = {
    shippingCost: window.shippingCost || 70000,
    freeShippingThreshold: window.freeShippingThreshold || 500000
  };
  
  // Initialize order summary
  renderOrderSummary();
  
  function renderOrderSummary() {
    const orderSummary = document.getElementById('order-summary');
    const subtotalEl = document.getElementById('subtotal');
    const shippingEl = document.getElementById('shipping');
    const totalEl = document.getElementById('total');
    
    if (cart.length === 0) {
      orderSummary.innerHTML = `
        <div class="text-center py-4">
          <i class="fas fa-shopping-cart text-2xl text-gray-300 mb-2"></i>
          <p class="text-gray-600 text-sm">سبد خرید شما خالی است</p>
        </div>
      `;
      return;
    }
    
    // Render cart items
    orderSummary.innerHTML = cart.map(item => `
      <div class="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
        <div class="w-10 h-10 bg-gradient-to-br from-pink-200 to-purple-200 rounded-lg flex items-center justify-center flex-shrink-0">
          ${item.image ? `<img src="${item.image}" alt="${item.name}" class="w-full h-full object-cover rounded-lg">` : `<i class="fas fa-image text-gray-400"></i>`}
        </div>
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-sm line-clamp-1">${item.name}</h4>
          <p class="text-purple-600 text-xs">${item.price ? item.price.toLocaleString() : '0'} تومان × ${item.quantity}</p>
        </div>
        <div class="text-left">
          <span class="font-bold text-sm">${((item.price || 0) * item.quantity).toLocaleString()} تومان</span>
        </div>
      </div>
    `).join('');
    
    // Calculate totals
    const subtotal = cart.reduce((total, item) => total + ((item.price || 0) * item.quantity), 0);
    const shipping = subtotal > shippingSettings.freeShippingThreshold ? 0 : shippingSettings.shippingCost;
    const total = subtotal + shipping;
    
    // Update summary
    if (subtotalEl) subtotalEl.textContent = subtotal.toLocaleString() + ' تومان';
    if (shippingEl) shippingEl.textContent = shipping === 0 ? 'رایگان' : shipping.toLocaleString() + ' تومان';
    if (totalEl) totalEl.textContent = total.toLocaleString() + ' تومان';
  }
  
  // Handle form submission
  document.getElementById('checkout-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submit-order');
    const submitText = document.getElementById('submit-text');
    const loadingText = document.getElementById('loading-text');
    
    // Show loading state
    submitBtn.disabled = true;
    submitText.classList.add('hidden');
    loadingText.classList.remove('hidden');
    
    try {
      const formData = new FormData(this);
      formData.append('cart_data', JSON.stringify(cart));
      
      const response = await fetch('/shop/process-order/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCsrfToken()
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Clear cart
        localStorage.removeItem('cart');
        
        // Show success message
        showNotification(result.message, 'success');
        
        // Redirect to order detail
        setTimeout(() => {
          window.location.href = result.redirect_url;
        }, 2000);
      } else {
        showNotification(result.message, 'error');
      }
    } catch (error) {
      console.error('Error processing order:', error);
      showNotification('خطا در پردازش سفارش. لطفاً دوباره تلاش کنید.', 'error');
    } finally {
      // Reset button state
      submitBtn.disabled = false;
      submitText.classList.remove('hidden');
      loadingText.classList.add('hidden');
    }
  });
  
  function getCsrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }
  
  function showNotification(message, type = 'info') {
    // Use existing notification system
    if (typeof window.showNotification === 'function') {
      window.showNotification(message, type);
    } else {
      alert(message);
    }
  }
});
