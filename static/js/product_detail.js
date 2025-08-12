/* Product Detail Page JS */
(function() {
  function toPersianNumber(num) {
    const map = ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
    return String(num).replace(/\d/g, d => map[d]);
  }

  function formatPrice(price) {
    const formatted = String(price).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return toPersianNumber(formatted);
  }

  let currentImageIndex = 0;
  let productImages = [];

  function updateThumbnails() {
    const thumbEls = document.querySelectorAll('#product-detail .thumbnail-img');
    thumbEls.forEach((el, idx) => {
      if (idx === currentImageIndex) el.classList.add('border-purple-500');
      else el.classList.remove('border-purple-500');
    });
  }

  function updateImageCounter() {
    const el = document.querySelector('#product-detail #current-image-number');
    if (el) el.textContent = currentImageIndex + 1;
  }

  function changeImageByIndex(nextIndex) {
    if (!productImages.length) return;
    currentImageIndex = (nextIndex + productImages.length) % productImages.length;
    pdChangeMainImage(productImages[currentImageIndex]);
  }

  function pdPreviousImage() { changeImageByIndex(currentImageIndex - 1); }
  function pdNextImage() { changeImageByIndex(currentImageIndex + 1); }

  function pdChangeMainImage(imageUrl) {
    const mainImage = document.getElementById('main-image-src');
    if (!mainImage) return;
    const nextUrl = imageUrl + (imageUrl.includes('?') ? '&' : '?') + 'v=' + Date.now();
    const preload = new Image();
    preload.onload = function() {
      mainImage.style.opacity = '0';
      setTimeout(() => {
        mainImage.src = nextUrl;
        mainImage.style.opacity = '1';
        const idx = productImages.indexOf(imageUrl);
        if (idx !== -1) currentImageIndex = idx;
        updateThumbnails();
        updateImageCounter();
      }, 50);
    };
    preload.onerror = function() { mainImage.src = nextUrl; };
    preload.src = nextUrl;
  }

  function wireUp() {
    const root = document.getElementById('product-detail');
    if (!root) return;
    try {
      const imagesAttr = root.getAttribute('data-images');
      if (imagesAttr) {
        // imagesAttr is like ["/a","/b"] (already JSON-like), but ensure parse safety
        productImages = JSON.parse(imagesAttr.replace(/'/g, '"'));
      }
    } catch (e) {
      productImages = [];
    }

    const prevBtn = document.getElementById('btn-prev');
    const nextBtn = document.getElementById('btn-next');
    if (prevBtn) prevBtn.addEventListener('click', pdPreviousImage);
    if (nextBtn) nextBtn.addEventListener('click', pdNextImage);

    document.querySelectorAll('#product-detail .thumbnail-img').forEach((el, idx) => {
      el.addEventListener('click', () => pdChangeMainImage(productImages[idx]));
    });

    // Price formatting
    const currentPriceElement = document.getElementById('current-price');
    const originalPriceElement = document.getElementById('original-price');
    if (currentPriceElement) {
      // Prefer data attribute to avoid parsing localized text
      const dataPriceAttr = currentPriceElement.getAttribute('data-price');
      const price = dataPriceAttr ? parseInt(dataPriceAttr) : parseInt(String(currentPriceElement.textContent).replace(/[^\d]/g, ''));
      currentPriceElement.textContent = formatPrice(price);
    }
    if (originalPriceElement) {
      const dataOriginalAttr = originalPriceElement.getAttribute('data-price');
      const originalPrice = dataOriginalAttr ? parseInt(dataOriginalAttr) : parseInt(String(originalPriceElement.textContent).replace(/[^\d]/g, ''));
      originalPriceElement.textContent = formatPrice(originalPrice) + ' تومان';
    }

    // Comments
    const ratingStars = document.querySelectorAll('#rating-stars i');
    const ratingInput = document.getElementById('rating-input');
    const showCommentBtn = document.getElementById('show-comment-form');
    const commentFormContainer = document.getElementById('comment-form-container');
    const cancelCommentBtn = document.getElementById('cancel-comment');
    const commentForm = document.getElementById('comment-form');

    if (showCommentBtn && commentFormContainer) {
      showCommentBtn.addEventListener('click', function() {
        commentFormContainer.classList.remove('hidden');
        this.parentElement.classList.add('hidden');
      });
    }
    if (cancelCommentBtn && showCommentBtn) {
      cancelCommentBtn.addEventListener('click', function() {
        commentFormContainer.classList.add('hidden');
        showCommentBtn.parentElement.classList.remove('hidden');
        if (commentForm) commentForm.reset();
        if (ratingInput) ratingInput.value = '';
        ratingStars.forEach(star => { star.classList.remove('fas'); star.classList.add('far'); });
      });
    }
    ratingStars.forEach(star => {
      star.addEventListener('click', function() {
        const rating = this.getAttribute('data-rating');
        if (ratingInput) ratingInput.value = rating;
        ratingStars.forEach((s, index) => {
          if (index < rating) { s.classList.remove('far'); s.classList.add('fas'); }
          else { s.classList.remove('fas'); s.classList.add('far'); }
        });
      });
    });

    if (commentForm) {
      commentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const rating = ratingInput ? ratingInput.value : '';
        const comment = this.querySelector('textarea[name="comment"]').value;
        if (!rating || !comment.trim()) return;
        const formData = new FormData();
        formData.append('rating', rating);
        formData.append('comment', comment);
        const productId = root.dataset.productId;
        fetch(`/shop/product/${productId}/comment/`, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).then(resp => {
          if (resp.ok) { window.location.reload(); throw 'reload'; }
          return resp.json().then(d => { if (d && d.success) { window.location.reload(); throw 'reload'; } });
        }).catch(() => {});
      });
    }
    

    // Tabs
    function showProductTab(tabName) {
      document.querySelectorAll('#product-detail .product-tab-content').forEach(el => el.classList.remove('active'));
      const selected = document.getElementById(`${tabName}-tab`);
      if (selected) selected.classList.add('active');
      document.querySelectorAll('#product-detail .product-tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.querySelector(`#product-detail .product-tab-btn[data-tab-target="${tabName}"]`);
      if (activeBtn) activeBtn.classList.add('active');
      const tabsSection = document.getElementById('details-tabs');
      if (tabsSection) tabsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    document.querySelectorAll('#product-detail .product-tab-btn[data-tab-target]').forEach(btn => {
      btn.addEventListener('click', function() {
        const target = this.getAttribute('data-tab-target');
        if (target) showProductTab(target);
      });
    });

    // Quantity controls
    const qtyInput = document.getElementById('quantity');
    const qtyDec = document.getElementById('qty-decrease');
    const qtyInc = document.getElementById('qty-increase');
    if (qtyDec && qtyInput) {
      qtyDec.addEventListener('click', function() {
        const current = parseInt(qtyInput.value || '1');
        if (current > 1) qtyInput.value = current - 1;
      });
    }
    if (qtyInc && qtyInput) {
      qtyInc.addEventListener('click', function() {
        const current = parseInt(qtyInput.value || '1');
        const max = parseInt(qtyInput.getAttribute('max') || '9999');
        if (current < max) qtyInput.value = current + 1;
      });
    }

    // Notification
    function showNotification(message, type = 'success') {
      const note = document.createElement('div');
      const bg = type === 'success' ? 'bg-green-500' : 'bg-red-500';
      note.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transition-all duration-300 transform translate-x-full ${bg}`;
      note.textContent = message;
      document.body.appendChild(note);
      setTimeout(() => note.classList.remove('translate-x-full'), 50);
      setTimeout(() => { note.classList.add('translate-x-full'); setTimeout(() => note.remove(), 300); }, 2500);
    }

    // Cart/Wishlist buttons
    const addToCartBtn = document.getElementById('btn-add-to-cart');
    const addToWishlistBtn = document.getElementById('btn-add-to-wishlist');
    if (addToCartBtn) {
      addToCartBtn.addEventListener('click', async function() {
        const productId = parseInt(root.dataset.productId);
        const quantity = qtyInput ? parseInt(qtyInput.value || '1') : 1;
        try {
          // تلاش برای ارسال به بک‌اند درصورت لاگین
          const resp = await fetch('/shop/api/add-to-cart/', {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ product_id: productId, quantity })
          });
          if (resp.ok) {
            const data = await resp.json();
            // در هر صورت شمارنده را به صورت خوش‌بینانه آپدیت می‌کنیم
            const countEl = document.getElementById('cart-count');
            if (countEl && data && typeof data.cart_items_count !== 'undefined') {
              countEl.textContent = data.cart_items_count;
            }
          } else {
            // اگر کاربر لاگین نیست یا خطا بود، در لوکال کار کن
            addToCartFallback(productId, quantity);
          }
        } catch (e) {
          addToCartFallback(productId, quantity);
        }
        showNotification('محصول به سبد خرید اضافه شد', 'success');
      });
    }

    function addToCartFallback(productId, quantity) {
      try {
        // از محصولات موجود در صفحه برای ساخت آیتم استفاده می‌کنیم
        const priceText = document.getElementById('current-price')?.textContent?.replace(/[^\d]/g, '') || '0';
        const price = parseInt(priceText) || 0;
        const name = document.querySelector('#product-detail h1')?.textContent?.trim() || 'محصول';
        const image = document.getElementById('main-image-src')?.getAttribute('src') || null;
        const raw = localStorage.getItem('cart') || '[]';
        const cart = JSON.parse(raw);
        const existing = cart.find(it => it.id === productId);
        if (existing) existing.quantity += quantity; else cart.push({ id: productId, name, price, quantity, image, color: 'from-pink-200 to-purple-200', iconColor: 'text-gray-400' });
        localStorage.setItem('cart', JSON.stringify(cart));
        const countEl = document.getElementById('cart-count');
        if (countEl) {
          const count = cart.reduce((t, it) => t + it.quantity, 0);
          countEl.textContent = count;
        }
      } catch (_) {}
    }
    if (addToWishlistBtn) {
      addToWishlistBtn.addEventListener('click', async function() {
        const productId = root.dataset.productId;
        try {
          const resp = await fetch('/shop/api/toggle-wishlist/', {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: new URLSearchParams({ product_id: productId })
          });
          if (resp.ok) {
            const data = await resp.json();
            showNotification(data.added ? 'به علاقه‌مندی‌ها اضافه شد' : 'از علاقه‌مندی‌ها حذف شد', 'success');
            return;
          }
        } catch (_) {}
        showNotification('برای استفاده از علاقه‌مندی‌ها وارد شوید', 'error');
      });
    }
  }

  document.addEventListener('DOMContentLoaded', wireUp);
})();

