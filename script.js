// Global state management
let isLoggedIn = false;
let currentUser = null;
let cart = [];
let allProducts = [];
let filteredProducts = [];

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

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in (in a real app, this would check localStorage or cookies)
    checkLoginStatus();
    
    // Load cart from localStorage
    loadCart();
    
    // Initialize products data
    initializeProducts();
    
    // Add click outside listener for dropdown
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.profile-dropdown')) {
            closeDropdown();
        }
    });
    
    // Initialize search functionality
    initializeSearch();
});

// Check login status
function checkLoginStatus() {
    // In a real app, this would check localStorage, cookies, or make an API call
    const savedUser = localStorage.getItem('genricycle_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        isLoggedIn = true;
        updateUI();
    }
}

// Update UI based on login status
function updateUI() {
    if (isLoggedIn) {
        authButtons.style.display = 'none';
        profileDropdown.style.display = 'block';
        profileName.textContent = currentUser.name;
    } else {
        authButtons.style.display = 'flex';
        profileDropdown.style.display = 'none';
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
function initializeProducts() {
    allProducts = [
        {
            id: 'chestal',
            name: 'Chestal Cold & Cough Relief',
            description: 'Homeopathic medicine for nasal & chest congestion, runny nose, and cough relief. Non-drowsy and dye-free.',
            price: 299,
            originalPrice: 399,
            rating: 4.2,
            reviews: 128,
            category: 'Homeopathic',
            image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'paracetamol',
            name: 'Paracetamol 500mg Tablets',
            description: 'Effective pain relief and fever reducer. Bell\'s Healthcare quality tablets for adults and children.',
            price: 45,
            originalPrice: 60,
            rating: 4.8,
            reviews: 256,
            category: 'Pain Relief',
            image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'ciplactin',
            name: 'Ciplactin (Cyproheptadine)',
            description: 'Antihistamine tablets for allergy relief, appetite stimulation, and motion sickness. Trusted Cipla quality.',
            price: 85,
            originalPrice: 120,
            rating: 4.1,
            reviews: 89,
            category: 'Antihistamine',
            image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'insulin',
            name: 'Generic Semglee Insulin Glargine',
            description: 'Long-acting insulin injection for diabetes management. 100 units/mL concentration for subcutaneous use.',
            price: 1250,
            originalPrice: 1800,
            rating: 4.6,
            reviews: 342,
            category: 'Prescription',
            image: 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'betadine',
            name: 'Betadine Povidone-Iodine Ointment',
            description: '10% w/w antiseptic ointment for wound care and skin disinfection. Effective against bacteria, fungi, and viruses.',
            price: 180,
            originalPrice: 250,
            rating: 4.3,
            reviews: 167,
            category: 'Antiseptic',
            image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'amoxicillin',
            name: 'Amoxicillin 500mg Capsules',
            description: 'Broad-spectrum antibiotic for bacterial infections. Effective against respiratory, urinary, and skin infections.',
            price: 120,
            originalPrice: 180,
            rating: 4.4,
            reviews: 203,
            category: 'Antibiotic',
            image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'omeprazole',
            name: 'Omeprazole 20mg Tablets',
            description: 'Proton pump inhibitor for acid reflux and stomach ulcers. Provides long-lasting relief from heartburn.',
            price: 95,
            originalPrice: 140,
            rating: 4.5,
            reviews: 189,
            category: 'Digestive',
            image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'metformin',
            name: 'Metformin 500mg Tablets',
            description: 'First-line treatment for Type 2 diabetes. Helps control blood sugar levels and improves insulin sensitivity.',
            price: 75,
            originalPrice: 110,
            rating: 4.3,
            reviews: 156,
            category: 'Diabetes',
            image: 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'ibuprofen',
            name: 'Ibuprofen 400mg Tablets',
            description: 'NSAID for pain relief, inflammation reduction, and fever control. Suitable for arthritis and muscle pain.',
            price: 65,
            originalPrice: 95,
            rating: 4.6,
            reviews: 234,
            category: 'Pain Relief',
            image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'vitamin-d',
            name: 'Vitamin D3 1000 IU Tablets',
            description: 'Essential vitamin for bone health, immune system support, and calcium absorption. Suitable for daily use.',
            price: 350,
            originalPrice: 450,
            rating: 4.7,
            reviews: 312,
            category: 'Vitamins',
            image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'atorvastatin',
            name: 'Atorvastatin 20mg Tablets',
            description: 'Statin medication for cholesterol management. Reduces LDL cholesterol and cardiovascular risk.',
            price: 180,
            originalPrice: 250,
            rating: 4.4,
            reviews: 178,
            category: 'Cardiovascular',
            image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'levothyroxine',
            name: 'Levothyroxine 50mcg Tablets',
            description: 'Thyroid hormone replacement therapy for hypothyroidism. Maintains normal thyroid function.',
            price: 125,
            originalPrice: 175,
            rating: 4.5,
            reviews: 145,
            category: 'Hormone',
            image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'losartan',
            name: 'Losartan 50mg Tablets',
            description: 'ACE inhibitor for blood pressure control and kidney protection. Reduces cardiovascular complications.',
            price: 110,
            originalPrice: 160,
            rating: 4.3,
            reviews: 167,
            category: 'Cardiovascular',
            image: 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'multivitamin',
            name: 'Multivitamin & Mineral Tablets',
            description: 'Complete daily nutrition supplement with essential vitamins and minerals for overall health.',
            price: 280,
            originalPrice: 380,
            rating: 4.6,
            reviews: 298,
            category: 'Vitamins',
            image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'calcium',
            name: 'Calcium Carbonate 500mg Tablets',
            description: 'Essential mineral for bone and teeth health. Prevents osteoporosis and supports muscle function.',
            price: 195,
            originalPrice: 275,
            rating: 4.4,
            reviews: 201,
            category: 'Minerals',
            image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'omeprazole-syrup',
            name: 'Omeprazole Oral Suspension',
            description: 'Liquid form of proton pump inhibitor for children and adults who have difficulty swallowing tablets.',
            price: 220,
            originalPrice: 320,
            rating: 4.5,
            reviews: 134,
            category: 'Digestive',
            image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'azithromycin',
            name: 'Azithromycin 250mg Tablets',
            description: 'Macrolide antibiotic for respiratory infections, skin infections, and sexually transmitted diseases.',
            price: 145,
            originalPrice: 210,
            rating: 4.2,
            reviews: 189,
            category: 'Antibiotic',
            image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'simvastatin',
            name: 'Simvastatin 20mg Tablets',
            description: 'HMG-CoA reductase inhibitor for cholesterol management. Reduces risk of heart attack and stroke.',
            price: 165,
            originalPrice: 235,
            rating: 4.4,
            reviews: 156,
            category: 'Cardiovascular',
            image: 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'vitamin-b12',
            name: 'Vitamin B12 1000mcg Tablets',
            description: 'Essential B-vitamin for nerve function, red blood cell formation, and energy metabolism.',
            price: 320,
            originalPrice: 420,
            rating: 4.7,
            reviews: 267,
            category: 'Vitamins',
            image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'
        },
        {
            id: 'diclofenac',
            name: 'Diclofenac 50mg Tablets',
            description: 'NSAID for pain relief and inflammation reduction. Effective for arthritis, muscle pain, and headaches.',
            price: 85,
            originalPrice: 125,
            rating: 4.3,
            reviews: 198,
            category: 'Pain Relief',
            image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'
        }
    ];
    filteredProducts = [...allProducts];
}

function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    applyFilters(query);
}

function applyFilters(searchQuery = '') {
    let filtered = [...allProducts];
    
    // Show/hide filters based on search
    const filterContainer = document.getElementById('filterContainer');
    if (searchQuery.trim()) {
        filterContainer.style.display = 'flex';
    } else {
        filterContainer.style.display = 'none';
    }
    
    // Apply search filter
    if (searchQuery) {
        filtered = filtered.filter(product => 
            product.name.toLowerCase().includes(searchQuery) ||
            product.description.toLowerCase().includes(searchQuery) ||
            product.category.toLowerCase().includes(searchQuery)
        );
    }
    
    // Apply price filter
    const priceFilter = document.getElementById('priceFilter').value;
    if (priceFilter === 'low-high') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (priceFilter === 'high-low') {
        filtered.sort((a, b) => b.price - a.price);
    }
    
    // Apply rating filter
    const ratingFilter = document.getElementById('ratingFilter').value;
    if (ratingFilter === 'high-rating') {
        filtered = filtered.filter(product => product.rating >= 4.5);
    }
    
    filteredProducts = filtered;
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
            <img src="${product.image}" alt="${product.name}">
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
            <button class="btn btn-primary add-to-cart" onclick="addToCart('${product.id}', '${product.name}', ${product.price})">
                <i class="fas fa-shopping-cart"></i> Add to Cart
            </button>
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
    const hasFilters = searchInput.value.trim() || 
                      document.getElementById('priceFilter').value || 
                      document.getElementById('ratingFilter').value;
    
    if (hasFilters) {
        searchResultsInfo.style.display = 'flex';
        resultsCount.textContent = `${filteredProducts.length} result${filteredProducts.length !== 1 ? 's' : ''} found`;
    } else {
        searchResultsInfo.style.display = 'none';
    }
}

function clearFilters() {
    searchInput.value = '';
    document.getElementById('priceFilter').value = '';
    document.getElementById('ratingFilter').value = '';
    document.getElementById('filterContainer').style.display = 'none';
    filteredProducts = [...allProducts];
    displayProducts();
    updateSearchResultsInfo();
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
document.getElementById('forgotModal').querySelector('form').addEventListener('submit', function(e) {
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

// Login functionality
document.getElementById('loginModal').querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Simple validation
    if (!email || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    // Simulate login (in a real app, this would make an API call)
    if (email && password) {
        currentUser = {
            name: email.split('@')[0],
            email: email
        };
        
        isLoggedIn = true;
        localStorage.setItem('genricycle_user', JSON.stringify(currentUser));
        
        closeModal('loginModal');
        updateUI();
        
        // Clear form
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
        
        showNotification('Login successful!', 'success');
    } else {
        alert('Invalid credentials');
    }
});

// Signup functionality
document.getElementById('signupModal').querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    // Simple validation
    if (!name || !email || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }
    
    // Simulate signup (in a real app, this would make an API call)
    currentUser = {
        name: name,
        email: email
    };
    
    isLoggedIn = true;
    localStorage.setItem('genricycle_user', JSON.stringify(currentUser));
    
    closeModal('signupModal');
    updateUI();
    
    // Clear form
    document.getElementById('signupName').value = '';
    document.getElementById('signupEmail').value = '';
    document.getElementById('signupPassword').value = '';
    
    showNotification('Account created successfully!', 'success');
});

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

function addToCart(productId, productName, price) {
    if (!isLoggedIn) {
        showNotification('Please login to add items to cart', 'error');
        showLoginModal();
        return;
    }
    
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: price,
            quantity: 1
        });
    }
    
    saveCart();
    showNotification(`${productName} added to cart!`, 'success');
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

function validatePassword(password) {
    return password.length >= 6;
}

// Add real-time validation to forms
document.getElementById('loginEmail').addEventListener('blur', function() {
    const email = this.value;
    if (email && !validateEmail(email)) {
        this.style.borderColor = '#f44336';
    } else {
        this.style.borderColor = '#e0e0e0';
    }
});

document.getElementById('signupEmail').addEventListener('blur', function() {
    const email = this.value;
    if (email && !validateEmail(email)) {
        this.style.borderColor = '#f44336';
    } else {
        this.style.borderColor = '#e0e0e0';
    }
});

document.getElementById('signupPassword').addEventListener('input', function() {
    const password = this.value;
    if (password && !validatePassword(password)) {
        this.style.borderColor = '#f44336';
    } else {
        this.style.borderColor = '#e0e0e0';
    }
});
