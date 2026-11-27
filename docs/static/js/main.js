/**
 * TORENT DISTRIBUTION - MAIN JAVASCRIPT
 * Unified Products with Variations (5L, 10L, 20L, 50L / 500ml, 1L), Subcategory Filters, Cart
 */

let allProducts = [];
let cart = [];
let currentCategory = 'ALL';
let currentSubcategory = 'ALL';
let currentSearch = '';
let currentSort = 'default';

// Current modal state
let currentModalProduct = null;
let currentModalSize = '';
let currentModalPrice = 0.0;
let currentModalSku = '';
let currentModalStock = 0;

const subcategoriesConfig = {
    "Pamant de Flori": {
        label: "Marcă pământ de flori:",
        allLabel: "Toate mărcile de pământ",
        items: ["Florasol", "Humiflor", "Nutrisol", "Plantasol", "Florimo"]
    },
    "Ingrasaminte": {
        label: "Marcă / Tip soluție nutritivă:",
        allLabel: "Toate soluțiile nutritive & îngrășămintele",
        items: ["Vitaflora", "Florasol", "Humiflor", "Solide"]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initCart();
    initProductsData();
    initFiltersAndSearch();
    initModals();
    initCookieBanner();
});

function initCookieBanner() {
    const banner = document.getElementById('cookieConsentBanner');
    if (!banner) return;
    if (!localStorage.getItem('torent_cookie_consent')) {
        banner.style.display = 'block';
    }
}

function setCookieConsent(choice) {
    localStorage.setItem('torent_cookie_consent', JSON.stringify({
        choice: choice,
        date: new Date().toISOString()
    }));
    const banner = document.getElementById('cookieConsentBanner');
    if (banner) banner.style.display = 'none';
    showToast(choice === 'all' ? 'Preferințele cookies au fost salvate (toate acceptate).' : 'Preferințele cookies au fost salvate (doar esențiale).', 'info', 2500);
}

function openCookieBanner() {
    const banner = document.getElementById('cookieConsentBanner');
    if (banner) banner.style.display = 'block';
}

// Load products data from API so we have full variation trees
async function initProductsData() {
    try {
        const tokenMeta = document.querySelector('meta[name="x-catalog-token"]');
        const token = tokenMeta ? tokenMeta.getAttribute('content') : '';
        const resp = await fetch('/torent-distribution-webshop/api/products.json', {
            headers: {
                'X-Catalog-Token': token,
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        if (!resp.ok) throw new Error('Catalog API restricted');
        const data = await resp.json();
        allProducts = data;

        // Map DOM elements to products
        allProducts.forEach(p => {
            p.element = document.querySelector(`.product-card[data-id="${p.id}"]`);
            if (!p.variations || p.variations.length === 0) {
                p.variations = [{ size: p.default_size || "Standard", price: p.price, stock: p.stock || 20, sku: `TD-${p.id}` }];
            }
        });
    } catch (e) {
        // Fallback: parse from DOM
        const cards = document.querySelectorAll('.product-card');
        allProducts = [];
        cards.forEach(card => {
            const pid = parseInt(card.dataset.id);
            allProducts.push({
                id: pid,
                name: card.dataset.name,
                category: card.dataset.category,
                subcategory: card.dataset.subcategory || '',
                price: parseFloat(card.dataset.price),
                stock: parseInt(card.dataset.stock) || 20,
                element: card,
                variations: [{ size: "Standard", price: parseFloat(card.dataset.price), stock: 20, sku: `TD-${pid}` }]
            });
        });
    }

    // Start rotating category card thumbnails every 3 seconds
    initCategoryThumbRotator();

    // Activate category if landed on /categorie/<slug>
    if (window.INITIAL_CATEGORY && window.INITIAL_CATEGORY !== 'ALL') {
        filterByCategory(window.INITIAL_CATEGORY);
    } else {
        // Initial filter apply (ALL mode -> hides prices on cards, shows CTA)
        applyFilters();
    }
}

function initCategoryThumbRotator() {
    const thumbImgs = document.querySelectorAll('.cat-thumb-img[data-cat-thumb]');
    thumbImgs.forEach(imgEl => {
        const catKey = imgEl.getAttribute('data-cat-thumb');
        if (!catKey) return;

        // Collect unique images from products in this category
        const imgs = [];
        const seen = new Set();
        allProducts.forEach(p => {
            if (p.category === catKey && p.image && !seen.has(p.image)) {
                seen.add(p.image);
                imgs.push(p.image);
            }
        });

        if (imgs.length === 0) return;

        // Immediately show first real image of this category
        let idx = 0;
        imgEl.src = imgs[0];

        if (imgs.length > 1) {
            setInterval(() => {
                idx = (idx + 1) % imgs.length;
                imgEl.style.opacity = '0.2';
                setTimeout(() => {
                    imgEl.src = imgs[idx];
                    imgEl.style.opacity = '1';
                }, 220);
            }, 3000);
        }
    });
}

// ---------------- Cart Functionality ---------------- //
function initCart() {
    const saved = localStorage.getItem('torent_shop_cart');
    if (saved) {
        try {
            cart = JSON.parse(saved);
        } catch (e) {
            cart = [];
        }
    }
    updateCartUI();

    // Drawer triggers
    const openBtn = document.getElementById('openCartBtn');
    const closeBtn = document.getElementById('closeCartBtn');
    const overlay = document.getElementById('cartOverlay');

    if (openBtn) openBtn.addEventListener('click', openCart);
    if (closeBtn) closeBtn.addEventListener('click', closeCart);
    if (overlay) overlay.addEventListener('click', closeCart);
}

function saveCart() {
    localStorage.setItem('torent_shop_cart', JSON.stringify(cart));
    updateCartUI();
}

function openCart() {
    document.getElementById('cartDrawer').classList.add('active');
    document.getElementById('cartOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeCart() {
    document.getElementById('cartDrawer').classList.remove('active');
    document.getElementById('cartOverlay').classList.remove('active');
    document.body.style.overflow = '';
}

function addToCart(productId, quantity = 1, size = null, price = null) {
    const prod = allProducts.find(p => p.id === productId);
    if (!prod) return;

    // Default to first variation if not specified
    const selectedVar = prod.variations.find(v => v.size === size) || prod.variations[0];
    const itemSize = size || selectedVar.size;
    const itemPrice = (price !== null) ? price : selectedVar.price;
    const itemKey = `${productId}_${itemSize}`;

    const displayName = (itemSize && itemSize !== "Standard" && !prod.name.includes(itemSize))
        ? `${prod.name} (${itemSize})`
        : prod.name;

    const cotaTva = (selectedVar && selectedVar.cota_tva !== undefined)
        ? Number(selectedVar.cota_tva)
        : (prod.cota_tva !== undefined ? Number(prod.cota_tva) : (prod.category === 'Ingrasaminte' ? 11 : 21));

    const existing = cart.find(item => item.cartKey === itemKey);
    if (existing) {
        existing.quantity += quantity;
        existing.cota_tva = cotaTva;
    } else {
        cart.push({
            cartKey: itemKey,
            id: productId,
            name: displayName,
            size: itemSize,
            sku: (selectedVar && selectedVar.sku) ? selectedVar.sku : `TD-${productId}`,
            cota_tva: cotaTva,
            price: itemPrice,
            image: prod.image,
            quantity: quantity
        });
    }

    saveCart();
    showToast(`"${displayName}" a fost adăugat în coș!`, 'success');
}

function updateQuantity(cartKey, delta) {
    const item = cart.find(i => i.cartKey === cartKey);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
        removeFromCart(cartKey);
    } else {
        saveCart();
    }
}

function removeFromCart(cartKey) {
    cart = cart.filter(i => i.cartKey !== cartKey);
    saveCart();
    showToast('Produsul a fost eliminat din coș.', 'info');
}

function updateCartUI() {
    const badge = document.getElementById('cartBadgeCount');
    const headerTotal = document.getElementById('cartHeaderTotal');
    const drawerCount = document.getElementById('cartDrawerCount');
    const itemsContainer = document.getElementById('cartItemsContainer');
    const subtotalEl = document.getElementById('cartSubtotal');
    const shippingEl = document.getElementById('cartShipping');
    const totalEl = document.getElementById('cartTotal');
    const shippingNotice = document.getElementById('shippingNotice');
    const checkoutTotalEl = document.getElementById('modalCheckoutTotal');

    const totalQty = cart.reduce((sum, item) => sum + item.quantity, 0);
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = (subtotal >= 150 || subtotal === 0) ? 0.00 : 19.00;
    const grandTotal = subtotal + shipping;

    // Exact per-item TVA back-calculation (supports mixed 11% + 21% carts)
    let totalTvaProduse = 0;
    const tvaByRate = {};
    cart.forEach(item => {
        const prodRef = allProducts.find(p => p.id === item.id);
        const cota = (item.cota_tva !== undefined)
            ? Number(item.cota_tva)
            : (prodRef && prodRef.cota_tva !== undefined ? Number(prodRef.cota_tva) : (prodRef && prodRef.category === 'Ingrasaminte' ? 11 : 21));
        const qty = Number(item.quantity || 1);
        const unitBrut = Number(item.price || 0);
        const unitNet = Math.round((unitBrut / (1 + cota / 100)) * 100) / 100;
        const valBrut = Math.round(unitBrut * qty * 100) / 100;
        const valNet = Math.round(unitNet * qty * 100) / 100;
        const valTva = Math.round((valBrut - valNet) * 100) / 100;
        totalTvaProduse += valTva;
        tvaByRate[cota] = (tvaByRate[cota] || 0) + valTva;
    });
    const rateKeys = Object.keys(tvaByRate).sort((a, b) => Number(a) - Number(b));
    let tvaText = `din care TVA: ${totalTvaProduse.toFixed(2)} RON`;
    if (rateKeys.length > 1) {
        const parts = rateKeys.map(r => `TVA ${r}%: ${tvaByRate[r].toFixed(2)} RON`);
        tvaText = `din care TVA: ${totalTvaProduse.toFixed(2)} RON (${parts.join(' + ')})`;
    }

    if (badge) badge.innerText = totalQty;
    if (headerTotal) headerTotal.innerText = `${subtotal.toFixed(2)} RON`;
    if (drawerCount) drawerCount.innerText = totalQty;
    if (subtotalEl) subtotalEl.innerText = `${subtotal.toFixed(2)} RON`;
    if (shippingEl) shippingEl.innerText = shipping === 0 ? 'GRATUIT' : `${shipping.toFixed(2)} RON`;
    if (totalEl) totalEl.innerText = `${grandTotal.toFixed(2)} RON`;
    if (checkoutTotalEl) checkoutTotalEl.innerText = `${grandTotal.toFixed(2)} RON`;
    const cartTvaEl = document.getElementById('cartTvaBreakdown');
    const checkoutTvaEl = document.getElementById('checkoutTvaBreakdown');
    if (cartTvaEl) cartTvaEl.innerText = tvaText;
    if (checkoutTvaEl) checkoutTvaEl.innerText = tvaText;

    if (shippingNotice) {
        if (subtotal >= 150) {
            shippingNotice.innerHTML = '<i class="fa-solid fa-circle-check"></i> Felicitări! Beneficiezi de <strong>Transport GRATUIT</strong>!';
            shippingNotice.style.background = '#dcfce7';
        } else {
            const diff = (150 - subtotal).toFixed(2);
            shippingNotice.innerHTML = `<i class="fa-solid fa-truck"></i> Mai adaugă produse de <strong>${diff} RON</strong> pentru transport gratuit!`;
            shippingNotice.style.background = '#ecfdf5';
        }
    }

    if (!itemsContainer) return;

    if (cart.length === 0) {
        itemsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px 10px; color: #94a3b8;">
                <i class="fa-solid fa-bag-shopping" style="font-size: 3rem; margin-bottom: 12px; opacity: 0.5;"></i>
                <h4 style="color: #475569; margin-bottom: 6px;">Coșul tău este gol</h4>
                <p style="font-size: 0.85rem;">Alege pământ de flori sau îngrășăminte pentru a plasa o comandă.</p>
            </div>
        `;
        const openCheckoutBtn = document.getElementById('openCheckoutModalBtn');
        if (openCheckoutBtn) openCheckoutBtn.disabled = true;
    } else {
        const openCheckoutBtn = document.getElementById('openCheckoutModalBtn');
        if (openCheckoutBtn) openCheckoutBtn.disabled = false;

        itemsContainer.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-thumb">
                    <img src="${item.image}" alt="${item.name}" onerror="this.src='/torent-distribution-webshop/static/images/products/pamant-de-flori-universal-plantasol-5l.webp'">
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">${(item.price * item.quantity).toFixed(2)} RON</div>
                    <div class="cart-item-qty-row">
                        <div class="qty-control">
                            <button type="button" onclick="updateQuantity('${item.cartKey}', -1)">-</button>
                            <span>${item.quantity}</span>
                            <button type="button" onclick="updateQuantity('${item.cartKey}', 1)">+</button>
                        </div>
                        <button type="button" class="btn-remove-item" onclick="removeFromCart('${item.cartKey}')">
                            <i class="fa-solid fa-trash-can"></i> Șterge
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

// ---------------- Filtering & Search ---------------- //
function initFiltersAndSearch() {
    // Nav links
    const navLinks = document.querySelectorAll('.nav-link[data-category]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const cat = link.dataset.category;
            filterByCategory(cat);
        });
    });

    // Subcat links in dropdown
    const subcatLinks = document.querySelectorAll('.subcat-link');
    subcatLinks.forEach(link => {
        link.addEventListener('click', () => {
            const cat = link.dataset.category;
            const subcat = link.dataset.subcat;
            filterByCategory(cat, subcat);
        });
    });

    // Main filter pills on page
    const pills = document.querySelectorAll('.filter-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            const cat = pill.dataset.cat;
            filterByCategory(cat);
        });
    });

    // Live Search
    const searchInput = document.getElementById('liveSearchInput');
    const clearBtn = document.getElementById('clearSearchBtn');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim().toLowerCase();
            if (clearBtn) clearBtn.style.display = currentSearch ? 'block' : 'none';
            applyFilters();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            currentSearch = '';
            clearBtn.style.display = 'none';
            applyFilters();
        });
    }

    // Sort select
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value;
            applyFilters();
        });
    }
}

function filterByCategory(category, subcategory = 'ALL') {
    currentCategory = category;
    currentSubcategory = subcategory;

    // Update active nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.dataset.category === category) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Update active category cards & breadcrumb name
    let activeDisplayName = category;
    document.querySelectorAll('.category-card').forEach(card => {
        if (card.dataset.cat === category) {
            card.classList.add('active');
            const h3 = card.querySelector('h3');
            if (h3) activeDisplayName = h3.innerText.trim();
        } else {
            card.classList.remove('active');
        }
    });

    // Show/hide compact breadcrumb when a specific category is selected
    const resetCatBtn = document.getElementById('resetCategoryBtn');
    const activeCatNameEl = document.getElementById('activeCategoryNameBadge');
    if (resetCatBtn) {
        resetCatBtn.style.display = (category === 'ALL') ? 'none' : 'inline-flex';
    }
    if (activeCatNameEl) {
        activeCatNameEl.innerText = activeDisplayName;
    }

    // Update Dynamic Subcategory container
    renderSubcategoryPills(category, subcategory);

    applyFilters();

    // Scroll smoothly to products if clicking from hero or footer
    const productsSection = document.getElementById('produse');
    if (productsSection && window.scrollY > 400) {
        productsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function renderSubcategoryPills(category, activeSubcat) {
    const wrap = document.getElementById('subcatFilterWrap');
    const titleEl = document.getElementById('subcatLabelTitle');
    const container = document.getElementById('subcatButtonsContainer');

    if (!wrap || !container) return;

    let conf = subcategoriesConfig[category];
    const dynItems = (window.DYNAMIC_SUBCATEGORIES && window.DYNAMIC_SUBCATEGORIES[category]) ? window.DYNAMIC_SUBCATEGORIES[category] : null;
    if (dynItems && dynItems.length > 0) {
        conf = {
            label: conf ? conf.label : `Subcategorii (${category}):`,
            allLabel: conf ? conf.allLabel : `Toate din ${category}`,
            items: dynItems
        };
    } else if (window.DYNAMIC_SUBCATEGORIES && !dynItems) {
        conf = null;
    }

    if (!conf || !conf.items || conf.items.length === 0) {
        // Categories without subcategories
        wrap.style.display = 'none';
        container.innerHTML = '';
        return;
    }

    wrap.style.display = 'flex';
    if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-filter"></i> ${conf.label}`;

    let html = `
        <button type="button" class="subcat-pill ${activeSubcat === 'ALL' ? 'active' : ''}" onclick="selectSubcategory('${category}', 'ALL')">
            <i class="fa-solid fa-layer-group"></i> ${conf.allLabel}
        </button>
    `;

    conf.items.forEach(sub => {
        const isActive = (activeSubcat.toLowerCase() === sub.toLowerCase());
        const icon = (category === 'Pamant de Flori') ? 'fa-seedling' : (sub === 'Solide' ? 'fa-cubes-stacked' : 'fa-droplet');
        html += `
            <button type="button" class="subcat-pill ${isActive ? 'active' : ''}" onclick="selectSubcategory('${category}', '${sub}')">
                <i class="fa-solid ${icon}"></i> ${sub}
            </button>
        `;
    });

    container.innerHTML = html;
}

function selectSubcategory(category, subcategory) {
    currentCategory = category;
    currentSubcategory = subcategory;

    // Highlight active subcat pill
    const container = document.getElementById('subcatButtonsContainer');
    if (container) {
        container.querySelectorAll('.subcat-pill').forEach(p => {
            p.classList.remove('active');
            if (subcategory === 'ALL' && p.innerText.includes('Toate')) {
                p.classList.add('active');
            } else if (p.innerText.includes(subcategory)) {
                p.classList.add('active');
            }
        });
    }

    applyFilters();
}

function applyFilters() {
    let visibleCount = 0;
    const grid = document.getElementById('productsGrid');
    const noResults = document.getElementById('noResultsBox');
    const badge = document.getElementById('resultsCountBadge');

    const isAllMode = (currentCategory === 'ALL');

    allProducts.forEach(p => {
        if (!p.element) return;

        let matchesCat = (currentCategory === 'ALL' || p.category === currentCategory);
        let matchesSubcat = (currentSubcategory === 'ALL' || (p.subcategory && p.subcategory.toLowerCase() === currentSubcategory.toLowerCase()));
        let matchesSearch = (!currentSearch || p.name.toLowerCase().includes(currentSearch));

        if (matchesCat && matchesSubcat && matchesSearch) {
            p.element.style.display = 'flex';
            visibleCount++;

            // Handle price visibility on cards according to user rule:
            // "Mikor ramesz a 'Toate' ra akkor viszont betoltheti az osszes termeket minden kiszerelesben, viszont itt nem kell feltuntetni az arakat, csak ha raklikkel a latogato a termek kepre."
            const priceValEl = p.element.querySelector('.card-price-display');
            const ctaEl = p.element.querySelector('.card-see-price-cta');

            if (isAllMode) {
                if (priceValEl) priceValEl.style.display = 'none';
                if (ctaEl) ctaEl.style.display = 'inline-flex';
            } else {
                if (priceValEl) priceValEl.style.display = 'block';
                if (ctaEl) ctaEl.style.display = 'none';
            }
        } else {
            p.element.style.display = 'none';
        }
    });

    // Sort visible cards
    const sorted = [...allProducts].sort((a, b) => {
        if (currentSort === 'price-asc') return a.price - b.price;
        if (currentSort === 'price-desc') return b.price - a.price;
        if (currentSort === 'name-asc') return a.name.localeCompare(b.name);
        return a.id - b.id; // default
    });

    sorted.forEach(p => {
        if (p.element) grid.appendChild(p.element);
    });

    if (badge) {
        badge.innerHTML = `Afișare <strong>${visibleCount}</strong> produse`;
    }

    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

function resetFilters() {
    const searchInput = document.getElementById('liveSearchInput');
    if (searchInput) searchInput.value = '';
    currentSearch = '';
    filterByCategory('ALL');
}

// ---------------- Modals & Quick View with Variations ---------------- //
function initModals() {
    // Quick view close
    const closeProdModal = document.getElementById('closeProductModal');
    if (closeProdModal) {
        closeProdModal.addEventListener('click', () => {
            document.getElementById('productModal').classList.remove('active');
        });
    }

    // Checkout modal triggers
    const openCheckoutBtn = document.getElementById('openCheckoutModalBtn');
    const closeCheckoutBtn = document.getElementById('closeCheckoutModal');
    const cancelCheckoutBtn = document.getElementById('cancelCheckoutBtn');

    if (openCheckoutBtn) {
        openCheckoutBtn.addEventListener('click', () => {
            if (cart.length === 0) return;
            closeCart();
            document.getElementById('checkoutModal').classList.add('active');
        });
    }

    if (closeCheckoutBtn) {
        closeCheckoutBtn.addEventListener('click', () => {
            document.getElementById('checkoutModal').classList.remove('active');
        });
    }

    if (cancelCheckoutBtn) {
        cancelCheckoutBtn.addEventListener('click', () => {
            document.getElementById('checkoutModal').classList.remove('active');
        });
    }

    // Modal Qty buttons
    const qtyMinus = document.getElementById('modalQtyMinus');
    const qtyPlus = document.getElementById('modalQtyPlus');
    const qtyInput = document.getElementById('modalQtyInput');

    if (qtyMinus && qtyInput) {
        qtyMinus.addEventListener('click', () => {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
    }
    if (qtyPlus && qtyInput) {
        qtyPlus.addEventListener('click', () => {
            let val = parseInt(qtyInput.value) || 1;
            if (val < 99) qtyInput.value = val + 1;
        });
    }

    // Modal Add To Cart
    const modalAddBtn = document.getElementById('modalAddToCartBtn');
    if (modalAddBtn) {
        modalAddBtn.addEventListener('click', () => {
            if (!currentModalProduct) return;
            const qty = parseInt(document.getElementById('modalQtyInput').value) || 1;
            addToCart(currentModalProduct.id, qty, currentModalSize, currentModalPrice);
            document.getElementById('productModal').classList.remove('active');
        });
    }

    // Checkout Form Submit
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const termsCheck = document.getElementById('acceptTermsCheck');
            const gdprCrmCheck = document.getElementById('acceptGdprCrmCheck');
            if (termsCheck && !termsCheck.checked) {
                showToast('Vă rugăm să acceptați Termenii și Condițiile și Politica GDPR.', 'error');
                return;
            }

            const submitBtn = document.getElementById('submitOrderBtn');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se trimite comanda...';

            const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const shipping = (subtotal >= 150) ? 0.00 : 19.00;
            const grandTotal = subtotal + shipping;

            const orderData = {
                customer: {
                    name: document.getElementById('custName').value.trim(),
                    phone: document.getElementById('custPhone').value.trim(),
                    email: document.getElementById('custEmail').value.trim(),
                    county: document.getElementById('custCounty').value.trim(),
                    city: document.getElementById('custCity').value.trim(),
                    address: document.getElementById('custAddress').value.trim()
                },
                payment_method: document.querySelector('input[name="paymentMethod"]:checked').value,
                items: cart,
                total: grandTotal,
                terms_accepted: termsCheck ? termsCheck.checked : true,
                gdpr_crm_consent: gdprCrmCheck ? gdprCrmCheck.checked : false
            };

            try {
                const resp = { ok: true, json: async () => ({ success: true, message: 'Comandă demo înregistrată cu succes (mod previzualizare statică GitHub Pages)!' }) }; if (false) await fetch('/api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(orderData)
                });
                const res = await resp.json();

                if (res.success) {
                    cart = [];
                    saveCart();
                    document.getElementById('checkoutModal').classList.remove('active');
                    showToast(res.message, 'success', 6000);
                    checkoutForm.reset();
                } else {
                    showToast(res.message || 'Eroare la trimiterea comenzii.', 'error');
                }
            } catch (err) {
                showToast('A apărut o eroare de conexiune. Vă rugăm reîncercați.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fa-solid fa-check"></i> Trimite Comanda (obligație de plată)';
            }
        });
    }
}

// Open Quick View Product with 1 Unified Image and Package Size Variations
function openProductQuickView(productId) {
    const prod = allProducts.find(p => p.id === productId);
    if (!prod) return;

    currentModalProduct = prod;

    // Header badge
    const badgeText = prod.subcategory ? `${prod.category} • ${prod.subcategory}` : prod.category;
    document.getElementById('modalProdCategory').innerText = badgeText;
    document.getElementById('modalProdTitle').innerText = prod.name;
    document.getElementById('modalProdImage').src = prod.image;
    document.getElementById('modalQtyInput').value = 1;

    // Rich description with collapsed state & "Vezi Detalii" toggle
    const descEl = document.getElementById('modalProdDesc');
    const toggleBtn = document.getElementById('modalToggleDescBtn');
    const fullPageLink = document.getElementById('modalFullPageLink');
    const fullDesc = prod.description || `${prod.name} oferă o calitate profesională superioară pentru horticultură și îngrijirea plantelor.`;
    
    descEl.innerText = fullDesc;
    descEl.classList.add('collapsed');
    
    if (toggleBtn) {
        if (fullDesc.length > 220) {
            toggleBtn.style.display = 'inline-flex';
            toggleBtn.innerHTML = '<i class="fa-solid fa-chevron-down"></i> Vezi Detalii';
        } else {
            toggleBtn.style.display = 'none';
            descEl.classList.remove('collapsed');
        }
    }
    if (fullPageLink) {
        fullPageLink.href = `/produs/${prod.id}`;
    }

    // Setup Variations
    const variationsBox = document.getElementById('modalVariationsBox');
    const buttonsGrid = document.getElementById('modalVariationButtons');

    if (prod.variations && prod.variations.length > 0) {
        variationsBox.style.display = 'block';

        // Select first variation as default
        const defaultVar = prod.variations[0];
        currentModalSize = defaultVar.size;
        currentModalPrice = defaultVar.price;
        currentModalSku = defaultVar.sku || `TD-${prod.id}`;
        currentModalStock = defaultVar.stock || 25;

        // Render variation buttons
        buttonsGrid.innerHTML = prod.variations.map((v, idx) => `
            <button type="button" 
                    class="var-btn ${idx === 0 ? 'active' : ''}" 
                    data-size="${v.size}" 
                    data-price="${v.price}"
                    data-sku="${v.sku || `TD-${prod.id}`}"
                    data-stock="${v.stock || 25}"
                    onclick="selectModalVariation(this)">
                <span class="var-btn-size">${v.size}</span>
                <span class="var-btn-price">${v.price.toFixed(2)} RON</span>
            </button>
        `).join('');

        // If only 1 generic variation like "Standard", we can hide the variations box
        if (prod.variations.length === 1 && prod.variations[0].size === "Standard") {
            variationsBox.style.display = 'none';
        }
    } else {
        variationsBox.style.display = 'none';
        currentModalSize = "Standard";
        currentModalPrice = prod.price;
        currentModalSku = `TD-${prod.id}`;
        currentModalStock = prod.stock || 20;
    }

    // Update Price display
    updateModalPriceDisplay();

    document.getElementById('productModal').classList.add('active');
}

function selectModalVariation(btn) {
    const parent = btn.parentElement;
    parent.querySelectorAll('.var-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    currentModalSize = btn.dataset.size;
    currentModalPrice = parseFloat(btn.dataset.price);
    currentModalSku = btn.dataset.sku;
    currentModalStock = parseInt(btn.dataset.stock) || 20;

    updateModalPriceDisplay();
}

function updateModalPriceDisplay() {
    document.getElementById('modalProdPrice').innerText = `${currentModalPrice.toFixed(2)} RON (TVA inclus)`;
    document.getElementById('modalProdSku').innerText = currentModalSku;
    document.getElementById('modalProdStock').innerText = currentModalStock;
}

function toggleModalDescription() {
    const descEl = document.getElementById('modalProdDesc');
    const toggleBtn = document.getElementById('modalToggleDescBtn');
    if (!descEl || !toggleBtn) return;

    const isCollapsed = descEl.classList.contains('collapsed');
    if (isCollapsed) {
        descEl.classList.remove('collapsed');
        toggleBtn.innerHTML = '<i class="fa-solid fa-chevron-up"></i> Ascunde Detalii';
    } else {
        descEl.classList.add('collapsed');
        toggleBtn.innerHTML = '<i class="fa-solid fa-chevron-down"></i> Vezi Detalii';
    }
}

// ---------------- Toast System ---------------- //
function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(15px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
