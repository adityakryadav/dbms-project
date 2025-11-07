// Global state management
let isLoggedIn = false;
let currentUser = null;
let cart = [];
let allProducts = [];
let filteredProducts = [];
const DEFAULT_VISIBLE_COUNT = 15;

// DOM elements
const authButtons = document.getElementById('authButtons');
const profileDropdown = document.getElementById('profileDropdown');
const dropdownMenu = document.getElementById('dropdownMenu');
const profileName = document.getElementById('profileName');
const searchInput = document.querySelector('.search-input');
const searchBtn = document.querySelector('.search-btn');
const productsGrid = document.getElementById('productsGrid');
const searchResultsInfo = document.getElementById('searchResultsInfo');
const resultsCount = document.getElementById('resultsCount');
const filtersSidebar = document.getElementById('filtersSidebar');
const welcomeSection = document.querySelector('.welcome-section');

// Initialize the app
document.addEventListener('DOMContentLoaded', async function() {
    // Check if user is logged in (in a real app, this would check localStorage or cookies)
    checkLoginStatus();
    
    // Load cart from localStorage
    loadCart();
    // Reflect cart count badge immediately
    updateCartUI();
    
    // Initialize products data
    await initializeProducts();

    // Initialize categories filter
    await initializeCategories();
    
    // Add click outside listener for dropdown
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.profile-dropdown')) {
            closeDropdown();
        }
    });
    
    // Initialize search functionality
    initializeSearch();

    // Navigate to Generic Medicines section by default
    const genericSection = document.getElementById('generic-medicines');
    if (genericSection) {
        genericSection.scrollIntoView({ behavior: 'auto', block: 'start' });
    }
});

// Check login status
function checkLoginStatus() {
    const savedUser = localStorage.getItem('genricycle_user') || localStorage.getItem('userData');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
        } catch (e) {
            currentUser = { name: 'User' };
        }
        isLoggedIn = true;
    } else {
        currentUser = null;
        isLoggedIn = false;
    }
    // Always update UI after checking status
    updateUI();
}

// Update UI based on login status
function updateUI() {
    const cartLinks = document.querySelectorAll('.cart-link');

    if (isLoggedIn) {
        if (authButtons) authButtons.style.display = 'none';
        if (profileDropdown) profileDropdown.style.display = 'block';
        if (profileName && currentUser && currentUser.name) profileName.textContent = currentUser.name;
        cartLinks.forEach(link => {
            if (link) link.style.display = 'block';
        });
    } else {
        if (authButtons) authButtons.style.display = 'flex';
        if (profileDropdown) profileDropdown.style.display = 'none';
        cartLinks.forEach(link => {
            if (link) link.style.display = 'none';
        });
    }
}

// Search functionality
function initializeSearch() {
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Real-time search as user types
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            applyFilters(query);
        });
    }
}

// Products data initialization
async function initializeProducts() {
    try {
        const res = await fetch('/api/medicines');
        const data = await res.json();
        let mapped = Array.isArray(data) ? data.map(m => ({
            id: m.slug || String(m.id),
            name: m.name,
            description: m.description || '',
            price: Number(m.price) || 0,
            originalPrice: Math.round((Number(m.price) || 0) * 1.25) || (Number(m.price) || 0),
            rating: 4.5,
            reviews: 120,
            category: m.category_name || 'General',
            brand: m.brand || 'Generic',
            image: m.image_url || 'https://via.placeholder.com/400x400?text=No+Image'
        })) : [];
        if (!mapped.length) throw new Error('Empty medicines list');
        allProducts = mapped;
    } catch (e) {
        console.warn('Falling back to built-in product list due to API error:', e);
        // Fallback default featured medicines
        allProducts = [
            { id: 'paracetamol-500', name: 'Paracetamol 500mg', description: 'Pain reliever and fever reducer', price: 35, originalPrice: 60, rating: 4.6, reviews: 214, category: 'Analgesic', brand: 'Generic', image: 'assets/images/OIP.webp' },
            { id: 'ibuprofen-200', name: 'Ibuprofen 200mg', description: 'NSAID for pain and inflammation', price: 65, originalPrice: 99, rating: 4.5, reviews: 182, category: 'NSAID', brand: 'Generic', image: 'assets/images/OIP%20(1).webp' },
            { id: 'amoxicillin-500', name: 'Amoxicillin 500mg', description: 'Antibiotic for bacterial infections', price: 120, originalPrice: 180, rating: 4.4, reviews: 156, category: 'Antibiotic', brand: 'Generic', image: 'assets/images/OIP%20(2).webp' },
            { id: 'cetirizine-10', name: 'Cetirizine 10mg', description: 'Antihistamine for allergies', price: 45, originalPrice: 70, rating: 4.5, reviews: 201, category: 'Antihistamine', brand: 'Generic', image: 'assets/images/OIP%20(3).webp' },
            { id: 'omeprazole-20', name: 'Omeprazole 20mg', description: 'Reduces stomach acid, treats GERD', price: 85, originalPrice: 129, rating: 4.6, reviews: 190, category: 'Antacid', brand: 'Generic', image: 'assets/images/download.webp' },
            { id: 'metformin-500', name: 'Metformin 500mg', description: 'Helps control blood sugar levels', price: 110, originalPrice: 160, rating: 4.5, reviews: 170, category: 'Antidiabetic', brand: 'Generic', image: 'assets/images/download%20(1).webp' },
            { id: 'azithromycin-250', name: 'Azithromycin 250mg', description: 'Antibiotic for various infections', price: 140, originalPrice: 199, rating: 4.4, reviews: 145, category: 'Antibiotic', brand: 'Generic', image: 'assets/images/download%20(2).webp' }
        ];
    }
    filteredProducts = getDefaultProducts();
    populateBrandOptions();
    displayProducts();
    updateSearchResultsInfo();
}

// Categories initialization
async function initializeCategories() {
    try {
        const res = await fetch('/api/categories');
        const cats = await res.json();
        const select = document.getElementById('categoryFilter');
        if (select) {
            select.innerHTML = '<option value="">All Categories</option>';
            (Array.isArray(cats) ? cats : []).forEach(c => {
                const opt = document.createElement('option');
                opt.value = (c.name || '').toLowerCase();
                opt.textContent = c.name || '';
                select.appendChild(opt);
            });
        }
    } catch (e) {
        const select = document.getElementById('categoryFilter');
        if (select) {
            const cats = Array.from(new Set(allProducts.map(p => p.category))).filter(Boolean).sort();
            select.innerHTML = '<option value="">All Categories</option>';
            cats.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name.toLowerCase();
                opt.textContent = name;
                select.appendChild(opt);
            });
        }
    }
}

function populateBrandOptions() {
    const brandSelect = document.getElementById('brandFilter');
    if (!brandSelect) return;
    const brands = Array.from(new Set(allProducts.map(p => p.brand))).filter(Boolean).sort();
    brands.forEach(brand => {
        const opt = document.createElement('option');
        opt.value = brand.toLowerCase();
        opt.textContent = brand;
        brandSelect.appendChild(opt);
    });
}

function getDefaultProducts() {
    return allProducts.slice(0, DEFAULT_VISIBLE_COUNT);
}

function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    applyFilters(query);
}

function applyFilters(searchQuery = '') {
    // Always pull the latest query if not explicitly passed
    const query = (searchQuery ?? '').toString().trim().toLowerCase() || (searchInput ? searchInput.value.trim().toLowerCase() : '');

    let filtered = [...allProducts];

    // Current filter values
    const priceValue = document.getElementById('priceFilter') ? document.getElementById('priceFilter').value : '';
    const ratingValue = document.getElementById('ratingFilter') ? document.getElementById('ratingFilter').value : '';
    const brandValue  = document.getElementById('brandFilter') ? document.getElementById('brandFilter').value : '';
    const offerValue  = document.getElementById('offerSort') ? document.getElementById('offerSort').value : '';
    const categoryValue = document.getElementById('categoryFilter') ? document.getElementById('categoryFilter').value : '';
    const hasActiveFilters = Boolean(priceValue || ratingValue || brandValue || offerValue || categoryValue);

    // Show/hide sidebar: visible when searching or filters active
    if (filtersSidebar) {
        if (query || hasActiveFilters) {
            filtersSidebar.style.display = 'block';
        } else if (!document.body.classList.contains('filters-forced-open')) {
            filtersSidebar.style.display = 'none';
        }
    }

    // 1) Search filter
    if (query) {
        filtered = filtered.filter(product =>
            product.name.toLowerCase().includes(query) ||
            product.description.toLowerCase().includes(query) ||
            product.category.toLowerCase().includes(query) ||
            (product.brand || '').toLowerCase().includes(query)
        );
    }

    // 2) Rating filter
    if (ratingValue === 'high-rating') {
        filtered = filtered.filter(product => product.rating >= 4.5);
    }

    // 3) Brand filter
    if (brandValue) {
        filtered = filtered.filter(product => (product.brand || '').toLowerCase() === brandValue);
    }

    // 3b) Category filter
    if (categoryValue) {
        filtered = filtered.filter(product => (product.category || '').toLowerCase() === categoryValue);
    }

    // 4) Sorting: offers OR price
    if (offerValue === 'best-offers') {
        filtered.sort((a, b) => {
            const discA = Math.round(((a.originalPrice - a.price) / a.originalPrice) * 100);
            const discB = Math.round(((b.originalPrice - b.price) / b.originalPrice) * 100);
            return discB - discA;
        });
    } else if (priceValue === 'low-high') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (priceValue === 'high-low') {
        filtered.sort((a, b) => b.price - a.price);
    }

    // Default view when nothing is applied
    if (!query && !hasActiveFilters) {
        filteredProducts = getDefaultProducts();
    } else {
        filteredProducts = filtered;
    }
    displayProducts();
    updateSearchResultsInfo();
}

function displayProducts() {
    if (!productsGrid) return;
    
    productsGrid.innerHTML = '';
    
    filteredProducts.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const discount = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);
    
    card.innerHTML = `
        <div class="product-image">
            <img src="${product.image}" alt="${product.name}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='https://via.placeholder.com/400x400?text=Image+Unavailable';">
            <div class="product-badge">${product.category}</div>
        </div>
        <div class="product-info">
            <h3 class="product-name">${product.name}</h3>
            <p class="product-description">${product.description}</p>
            <div class="product-rating">
                <div class="stars">
                    ${generateStars(product.rating)}
                </div>
                <span class="rating-text">${product.rating} (${product.reviews} reviews)</span>
            </div>
            <div class="product-price">
                <span class="current-price">₹${product.price}</span>
                <span class="original-price">₹${product.originalPrice}</span>
                <span class="discount">${discount}% OFF</span>
            </div>
            <div class="product-meta">
                <span class="product-brand">Brand: ${product.brand || 'Generic'}</span>
            </div>
            <div class="product-quantity">
                <input type="number" min="1" value="1" class="quantity-input" id="quantity-${product.id}">
                <button class="btn btn-primary add-to-cart" onclick="addToCart('${product.id}', '${product.name}', ${product.price}, document.getElementById('quantity-${product.id}').value)">
                    <i class="fas fa-shopping-cart"></i> Add to Cart
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function generateStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<span class="star filled">★</span>';
    }
    
    if (hasHalfStar) {
        stars += '<span class="star half">★</span>';
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<span class="star">★</span>';
    }
    
    return stars;
}

function updateSearchResultsInfo() {
    const hasQuery = searchInput ? searchInput.value.trim() : '';
    const priceValue = document.getElementById('priceFilter') ? document.getElementById('priceFilter').value : '';
    const ratingValue = document.getElementById('ratingFilter') ? document.getElementById('ratingFilter').value : '';
    const brandValue = document.getElementById('brandFilter') ? document.getElementById('brandFilter').value : '';
    const offerValue = document.getElementById('offerSort') ? document.getElementById('offerSort').value : '';
    const categoryValue = document.getElementById('categoryFilter') ? document.getElementById('categoryFilter').value : '';
    const hasFilters = Boolean(hasQuery || priceValue || ratingValue || brandValue || offerValue || categoryValue);

    if (searchResultsInfo) {
        if (hasFilters) {
            searchResultsInfo.style.display = 'flex';
            if (resultsCount) {
                resultsCount.textContent = `${filteredProducts.length} result${filteredProducts.length !== 1 ? 's' : ''} found`;
            }
        } else {
            searchResultsInfo.style.display = 'none';
        }
    }

    // Toggle welcome section visibility based on search/filters
    if (welcomeSection) {
        if (hasFilters) {
            welcomeSection.style.display = 'none';
        } else {
            welcomeSection.style.display = '';
        }
    }
}

function clearFilters() {
    searchInput.value = '';
    if (document.getElementById('priceFilter')) document.getElementById('priceFilter').value = '';
    if (document.getElementById('ratingFilter')) document.getElementById('ratingFilter').value = '';
    if (document.getElementById('brandFilter')) document.getElementById('brandFilter').value = '';
    if (document.getElementById('offerSort')) document.getElementById('offerSort').value = '';
    if (filtersSidebar) filtersSidebar.style.display = 'none';
    filteredProducts = getDefaultProducts();
    displayProducts();
    updateSearchResultsInfo();
}

// Toggle filters sidebar visibility manually
function toggleFiltersSidebar() {
    if (!filtersSidebar) return;
    const isVisible = filtersSidebar.style.display !== 'none';
    if (isVisible) {
        filtersSidebar.style.display = 'none';
        document.body.classList.remove('filters-forced-open');
    } else {
        filtersSidebar.style.display = 'block';
        document.body.classList.add('filters-forced-open');
    }
}

function showSearchSuggestions(query) {
    // In a real app, this would show dynamic suggestions
    const suggestions = [
        'Paracetamol', 'Aspirin', 'Ibuprofen', 'Amoxicillin', 'Metformin',
        'Omeprazole', 'Atorvastatin', 'Lisinopril', 'Metoprolol', 'Simvastatin'
    ];
    
    const filteredSuggestions = suggestions.filter(med => 
        med.toLowerCase().includes(query)
    );
    
    if (filteredSuggestions.length > 0) {
        console.log('Search suggestions:', filteredSuggestions);
    }
}

function hideSearchSuggestions() {
    // Hide suggestions when input is cleared
}

// Profile dropdown functions
function toggleProfileDropdown() {
    const trigger = document.querySelector('.profile-trigger');
    const isOpen = dropdownMenu.classList.contains('show');
    
    if (isOpen) {
        closeDropdown();
    } else {
        openDropdown();
    }
}

function openDropdown() {
    const trigger = document.querySelector('.profile-trigger');
    dropdownMenu.classList.add('show');
    trigger.classList.add('active');
}

function closeDropdown() {
    const trigger = document.querySelector('.profile-trigger');
    dropdownMenu.classList.remove('show');
    trigger.classList.remove('active');
}

// Modal functions
function showLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function showSignupModal() {
    const modal = document.getElementById('signupModal');
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function showForgotModal() {
    const modal = document.getElementById('forgotModal');
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
});

// Forgot password functionality
const forgotModalEl = document.getElementById('forgotModal');
if (forgotModalEl) {
    const forgotForm = forgotModalEl.querySelector('form');
    if (forgotForm) {
        forgotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('forgotEmail').value;
            if (!validateEmail(email)) {
                alert('Please enter a valid email');
                return;
            }
            closeModal('forgotModal');
            document.getElementById('forgotEmail').value = '';
            showNotification('Password reset link sent to your email', 'success');
        });
    }
}

// Login functionality
const loginModalEl = document.getElementById('loginModal');
if (loginModalEl) {
    const loginForm = loginModalEl.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            if (!email || !password) {
                alert('Please fill in all fields');
                return;
            }
            if (email && password) {
                currentUser = { name: email.split('@')[0], email };
                isLoggedIn = true;
                localStorage.setItem('genricycle_user', JSON.stringify(currentUser));
                closeModal('loginModal');
                updateUI();
                document.getElementById('loginEmail').value = '';
                document.getElementById('loginPassword').value = '';
                showNotification('Login successful!', 'success');
            } else {
                alert('Invalid credentials');
            }
        });
    }
}

// Signup functionality
const signupModalEl = document.getElementById('signupModal');
if (signupModalEl) {
    const signupForm = signupModalEl.querySelector('form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            if (!name || !email || !password) {
                alert('Please fill in all fields');
                return;
            }
            if (password.length < 6) {
                alert('Password must be at least 6 characters long');
                return;
            }
            const role = (document.getElementById('signupRole') && document.getElementById('signupRole').value) || 'user';
            currentUser = { name, email, role };
            isLoggedIn = true;
            localStorage.setItem('genricycle_user', JSON.stringify(currentUser));
            closeModal('signupModal');
            updateUI();
            document.getElementById('signupName').value = '';
            document.getElementById('signupEmail').value = '';
            document.getElementById('signupPassword').value = '';
            showNotification('Account created successfully!', 'success');
        });
    }
}

// Logout functionality
function logout() {
    isLoggedIn = false;
    currentUser = null;
    localStorage.removeItem('genricycle_user');
    updateUI();
    closeDropdown();
    showNotification('Logged out successfully!', 'info');
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 3000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Close dropdown with Escape key
    if (e.key === 'Escape') {
        closeDropdown();
        // Close any open modals
        document.querySelectorAll('.modal.show').forEach(modal => {
            closeModal(modal.id);
        });
    }
});

// Add loading states for buttons
function addLoadingState(button, text = 'Loading...') {
    const originalText = button.textContent;
    button.textContent = text;
    button.disabled = true;
    button.style.opacity = '0.7';
    
    return function removeLoadingState() {
        button.textContent = originalText;
        button.disabled = false;
        button.style.opacity = '1';
    };
}

// Cart functionality
function loadCart() {
    const savedCart = localStorage.getItem('genricycle_cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
    }
}

function saveCart() {
    localStorage.setItem('genricycle_cart', JSON.stringify(cart));
}

function addToCart(productId, productName, price, quantity = 1) {
    if (!isLoggedIn) {
        showNotification('Please login to add items to cart', 'error');
        showLoginModal();
        return;
    }
    
    // Convert quantity to number
    quantity = parseInt(quantity) || 1;
    
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: price,
            quantity: quantity
        });
    }
    
    saveCart();
    showNotification(`${quantity} ${productName} added to cart!`, 'success');
    updateCartUI();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartUI();
    showNotification('Item removed from cart', 'info');
}

function updateCartQuantity(productId, quantity) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            item.quantity = quantity;
            saveCart();
            updateCartUI();
        }
    }
}

function updateCartUI() {
    // Update cart count in header if cart icon exists
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'block' : 'none';
    }
}

function getCartTotal() {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

function getCartItems() {
    return cart;
}

// Enhanced form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// =========================
// Cart Modal & Checkout Flow
// =========================

function openCartModal() {
    if (!isLoggedIn) {
        showLoginModal();
        showNotification('Please log in to view your cart.', 'info');
        return;
    }
    const modal = document.getElementById('cartModal');
    if (!modal) {
        showNotification('Cart UI not available on this page', 'error');
        return;
    }
    // Default to Cart step
    switchCartStep('cart');
    renderCartItems();
    // Attach tab switches
    document.querySelectorAll('.step-tab').forEach(btn => {
        btn.onclick = () => switchCartStep(btn.getAttribute('data-step'));
    });
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function switchCartStep(step) {
    // Tabs
    document.querySelectorAll('.step-tab').forEach(t => t.classList.remove('active'));
    const activeTab = document.querySelector(`.step-tab[data-step="${step}"]`);
    if (activeTab) activeTab.classList.add('active');
    // Panels
    const panels = ['cartStep','paymentStep','deliveryStep'];
    panels.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id.toLowerCase().includes(step)) {
            el.classList.add('active');
            el.style.display = 'block';
        } else {
            el.classList.remove('active');
            el.style.display = 'none';
        }
    });
}

function renderCartItems() {
    const container = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if (!container) return;
    const items = getCartItems();
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="cart-empty">Your cart is empty.</div>';
        if (totalEl) totalEl.textContent = '0';
        return;
    }
    const rows = items.map(item => {
        const price = Number(item.price) || 0;
        const qty = Number(item.quantity) || 1;
        return `
            <div class="cart-row" data-id="${item.id}">
                <div class="item-name">${item.name}</div>
                <div class="item-price">₹${price}</div>
                <div>
                    <input type="number" min="1" class="qty-input" value="${qty}" data-id="${item.id}">
                </div>
                <button class="remove-btn" data-id="${item.id}">Remove</button>
            </div>
        `;
    }).join('');
    container.innerHTML = rows;
    if (totalEl) totalEl.textContent = getCartTotal();
    // Attach listeners
    container.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', e => {
            const id = e.target.getAttribute('data-id');
            const qty = Math.max(1, parseInt(e.target.value, 10) || 1);
            updateCartQuantity(id, qty);
            // Update totals and badge
            if (totalEl) totalEl.textContent = getCartTotal();
        });
    });
    container.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            const id = e.target.getAttribute('data-id');
            removeFromCart(id);
            renderCartItems();
        });
    });
}

function proceedToPayment() {
    const items = getCartItems();
    if (!items || items.length === 0) {
        showNotification('Add items to cart before payment', 'error');
        return;
    }
    switchCartStep('payment');
}

function confirmPayment() {
    const selected = document.querySelector('input[name="paymentMethod"]:checked');
    if (!selected) {
        showNotification('Please select a payment method', 'error');
        return;
    }
    // Simulate payment success
    const method = selected.value;
    showNotification(`Payment confirmed via ${method.toUpperCase()}`, 'success');

    // Create order from current cart
    const items = getCartItems();
    if (!items || items.length === 0) {
        showNotification('Cart is empty, cannot place order', 'error');
        return;
    }
    const order = {
        id: `ORD-${Date.now()}`,
        date: new Date().toISOString(),
        items: items.map(it => ({ id: it.id, name: it.name, price: Number(it.price)||0, quantity: Number(it.quantity)||1 })),
        total: getCartTotal(),
        status: 'processing',
        paymentMethod: method
    };

    // Persist order history
    const existingOrders = JSON.parse(localStorage.getItem('genricycle_orders') || '[]');
    existingOrders.unshift(order);
    localStorage.setItem('genricycle_orders', JSON.stringify(existingOrders));

    // Record transaction
    const transactions = JSON.parse(localStorage.getItem('genricycle_transactions') || '[]');
    transactions.unshift({
        id: order.id,
        type: 'purchase',
        title: `Order ${order.id}`,
        date: order.date,
        amount: order.total,
        status: 'completed',
        details: `${order.items.length} item(s)`
    });
    localStorage.setItem('genricycle_transactions', JSON.stringify(transactions));

    // Clear cart and update UI
    cart = [];
    saveCart();
    updateCartUI();
    renderCartItems();

    // Move to delivery step and show ETA
    switchCartStep('delivery');
    showDeliveryDetails();
}

function showDeliveryDetails() {
    const items = getCartItems();
    const itemCount = (items || []).reduce((s, it) => s + (Number(it.quantity) || 1), 0);
    const base = 15; // base minutes
    const perItem = 5; // per item minutes
    const eta = Math.min(60, base + (itemCount * perItem));
    const etaEl = document.getElementById('deliveryEta');
    const mapEl = document.getElementById('deliveryMap');
    if (etaEl) etaEl.textContent = `Estimated delivery: ${eta} mins`;
    if (mapEl) {
        const now = new Date();
        const arrival = new Date(now.getTime() + eta * 60000);
        const timeStr = arrival.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        mapEl.innerHTML = `
            <div style="text-align:center;">
                <p>Route from Warehouse → Your Address</p>
                <p>Expected by ${timeStr}</p>
                <div style="margin-top:8px;font-size:0.9rem;color:#555;">(Map preview placeholder)</div>
            </div>
        `;
    }
}

function validatePassword(password) {
    return password.length >= 6;
}

// Add real-time validation to forms
const loginEmailEl2 = document.getElementById('loginEmail');
if (loginEmailEl2) {
    loginEmailEl2.addEventListener('blur', function() {
        const email = this.value;
        if (email && !validateEmail(email)) {
            this.style.borderColor = '#f44336';
        } else {
            this.style.borderColor = '#e0e0e0';
        }
    });
}

const signupEmailEl2 = document.getElementById('signupEmail');
if (signupEmailEl2) {
    signupEmailEl2.addEventListener('blur', function() {
        const email = this.value;
        if (email && !validateEmail(email)) {
            this.style.borderColor = '#f44336';
        } else {
            this.style.borderColor = '#e0e0e0';
        }
    });
}

const signupPasswordEl2 = document.getElementById('signupPassword');
if (signupPasswordEl2) {
    signupPasswordEl2.addEventListener('input', function() {
        const password = this.value;
        if (password && !validatePassword(password)) {
            this.style.borderColor = '#f44336';
        } else {
            this.style.borderColor = '#e0e0e0';
        }
    });
}