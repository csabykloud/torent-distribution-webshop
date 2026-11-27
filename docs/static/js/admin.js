/**
 * TORENT DISTRIBUTION - ADMIN JAVASCRIPT
 * Image Upload & Delete, Product CRUD, Live Search & Filters
 */

document.addEventListener('DOMContentLoaded', () => {
    initImageUpload();
    initProductFilters();
    initGallerySearch();
});

// Tab switching
function switchAdminTab(tabId, btn) {
    document.querySelectorAll('.admin-tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.querySelectorAll('.admin-nav-item').forEach(b => {
        b.classList.remove('active');
    });

    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
    if (btn) btn.classList.add('active');

    // Show context-appropriate primary action button in topbar
    const addProdBtn = document.getElementById('topbarAddProdBtn');
    const addCatBtn = document.getElementById('topbarAddCatBtn');
    if (addProdBtn) addProdBtn.style.display = (tabId === 'productsTab') ? 'inline-flex' : 'none';
    if (addCatBtn) addCatBtn.style.display = (tabId === 'categoriesTab') ? 'inline-flex' : 'none';
}

// ---------------- Image Upload & Delete ---------------- //
function initImageUpload() {
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('imageFileInput');

    if (!dropzone || !fileInput) return;

    // Drag and drop events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.style.background = '#dcfce7';
            dropzone.style.borderColor = '#047857';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.style.background = '#f0fdf4';
            dropzone.style.borderColor = '#059669';
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const statusBox = document.getElementById('uploadStatusMessage');
    statusBox.style.display = 'block';
    statusBox.style.background = '#e0f2fe';
    statusBox.style.color = '#0369a1';
    statusBox.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Se încarcă imaginea <strong>${file.name}</strong>...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const resp = await fetch('/admin/api/image/upload', {
            method: 'POST',
            body: formData
        });
        const res = await resp.json();

        if (res.success) {
            statusBox.style.background = '#dcfce7';
            statusBox.style.color = '#15803d';
            statusBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${res.message}`;

            // Add new image card to grid
            prependImageToGallery(res.filename, res.url, (file.size / 1024).toFixed(1));
            updateImageCounters(1);
        } else {
            statusBox.style.background = '#fee2e2';
            statusBox.style.color = '#b91c1c';
            statusBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${res.message}`;
        }
    } catch (err) {
        statusBox.style.background = '#fee2e2';
        statusBox.style.color = '#b91c1c';
        statusBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Eroare la încărcare: ${err.message}`;
    }
}

function prependImageToGallery(filename, url, sizeKb) {
    const grid = document.getElementById('imagesGrid');
    if (!grid) return;

    const card = document.createElement('div');
    card.className = 'image-card';
    card.dataset.filename = filename.toLowerCase();
    card.innerHTML = `
        <div class="image-card-preview">
            <img src="${url}" alt="${filename}" loading="lazy">
        </div>
        <div class="image-card-body">
            <div class="image-card-name" title="${filename}">${filename}</div>
            <div class="image-card-meta">${sizeKb} KB</div>
            <div class="image-card-actions">
                <button class="btn-copy-url" onclick="copyImageUrl('${url}')">
                    <i class="fa-solid fa-link"></i> Copiază URL
                </button>
                <button class="btn-delete-img" onclick="deleteImage('${filename}')" title="Șterge imaginea de pe disc">
                    <i class="fa-solid fa-trash"></i> Șterge
                </button>
            </div>
        </div>
    `;
    grid.prepend(card);

    // Also add to select in product modal
    const select = document.getElementById('prodImageSelect');
    if (select) {
        const opt = document.createElement('option');
        opt.value = url;
        opt.innerText = filename;
        select.appendChild(opt);
    }
}

async function deleteImage(filename) {
    if (!confirm(`Sigur doriți să ștergeți definitiv imaginea "${filename}" de pe disc?`)) {
        return;
    }

    try {
        const resp = await fetch('/admin/api/image/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        });
        const res = await resp.json();

        if (res.success) {
            // Remove card with animation
            const card = document.querySelector(`.image-card[data-filename="${filename.toLowerCase()}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                card.style.transition = 'all 0.3s ease';
                setTimeout(() => card.remove(), 300);
            }
            updateImageCounters(-1);
            alert(res.message);
        } else {
            alert(res.message || 'Eroare la ștergerea imaginii.');
        }
    } catch (err) {
        alert('Eroare de conexiune la ștergerea imaginii.');
    }
}

function updateImageCounters(delta) {
    const statEl = document.getElementById('statImgCount');
    const galEl = document.getElementById('galleryCount');
    if (statEl) {
        let val = parseInt(statEl.innerText) || 0;
        statEl.innerText = Math.max(0, val + delta);
    }
    if (galEl) {
        let val = parseInt(galEl.innerText) || 0;
        galEl.innerText = Math.max(0, val + delta);
    }
}

function copyImageUrl(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert(`Calea imaginii a fost copiată în clipboard:\n${url}`);
    }).catch(() => {
        prompt('Copiază manual calea imaginii:', url);
    });
}

function initGallerySearch() {
    const input = document.getElementById('gallerySearch');
    if (!input) return;

    input.addEventListener('input', (e) => {
        const term = e.target.value.trim().toLowerCase();
        const cards = document.querySelectorAll('.image-card');
        cards.forEach(card => {
            const fname = card.dataset.filename || '';
            card.style.display = fname.includes(term) ? 'flex' : 'none';
        });
    });
}

// ---------------- Product Management ---------------- //
function initProductFilters() {
    const searchInput = document.getElementById('adminProductSearch');
    const catSelect = document.getElementById('adminCategoryFilter');

    function applyAdminFilters() {
        const term = searchInput ? searchInput.value.trim().toLowerCase() : '';
        const cat = catSelect ? catSelect.value : 'ALL';
        const rows = document.querySelectorAll('#adminProductsTable tbody tr');

        rows.forEach(row => {
            const rowCat = row.dataset.category;
            const rowName = row.dataset.name || '';
            const matchesCat = (cat === 'ALL' || rowCat === cat);
            const matchesTerm = (!term || rowName.includes(term) || row.innerText.toLowerCase().includes(term));

            row.style.display = (matchesCat && matchesTerm) ? '' : 'none';
        });
    }

    if (searchInput) searchInput.addEventListener('input', applyAdminFilters);
    if (catSelect) catSelect.addEventListener('change', applyAdminFilters);
}

function updateSubcatOptions() {
    const cat = document.getElementById('prodCategory').value;
    const subInput = document.getElementById('prodSubcategory');
    if (!subInput) return;
    
    if (cat === 'Pamant de Flori') {
        subInput.placeholder = "ex: Florasol, Humiflor, Nutrisol, Plantasol, Florimo";
    } else if (cat === 'Ingrasaminte') {
        subInput.placeholder = "ex: Vitaflora, Florasol, Humiflor, Solide";
    } else {
        subInput.placeholder = "Opțional (lăsați gol)";
    }
}

function calcBrutCeilHalf(netVal, tvaPct) {
    const net = parseFloat(String(netVal).replace(',', '.'));
    const tva = parseFloat(String(tvaPct).replace(',', '.'));
    if (isNaN(net) || net < 0) return 0;
    const rawGross = Math.round((net * (1 + (isNaN(tva) ? 21 : tva) / 100)) * 100) / 100;
    return Math.ceil(Math.round(rawGross * 200) / 100) / 2;
}

function autoSuggestTvaByCategory() {
    const pid = document.getElementById('editProductId').value;
    if (pid) return; // Don't overwrite existing product's TVA when editing
    const cat = document.getElementById('prodCategory').value;
    const tvaSelect = document.getElementById('prodCotaTva');
    if (tvaSelect) {
        tvaSelect.value = (cat === 'Ingrasaminte') ? '11' : '21';
        refreshVariationBrutPreviews();
    }
}

function refreshVariationBrutPreviews() {
    const tvaSelect = document.getElementById('prodCotaTva');
    const tvaPct = tvaSelect ? parseFloat(tvaSelect.value) : 21;
    document.querySelectorAll('#variationRowsContainer .var-editor-row').forEach(row => {
        const netInput = row.querySelector('.var-price-input');
        const brutBadge = row.querySelector('.var-brut-preview');
        if (netInput && brutBadge) {
            const brut = calcBrutCeilHalf(netInput.value, tvaPct);
            brutBadge.innerText = brut > 0 ? `${brut.toFixed(2)} RON` : '0.00 RON';
        }
    });
}

async function addNewTvaRate() {
    const input = prompt('Introduceți noua cotă de TVA (procent numeric, ex: 9, 19, 5):');
    if (input === null) return;
    const trimmed = input.trim();
    if (!trimmed) return;

    try {
        const resp = await fetch('/admin/api/tva/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rate: trimmed })
        });
        const res = await resp.json();
        if (res.success && Array.isArray(res.tva_rates)) {
            window.ADMIN_TVA_RATES = res.tva_rates;
            // Immediately update every TVA dropdown on the page (table + modal)
            document.querySelectorAll('.admin-tva-select, #prodCotaTva').forEach(sel => {
                const currentVal = sel.value;
                sel.innerHTML = res.tva_rates.map(r => `<option value="${r}" ${String(r) === String(currentVal) ? 'selected' : ''}>${r}%</option>`).join('');
            });
            alert(res.message);
        } else {
            alert(res.message || 'Eroare la adăugarea cotei TVA.');
        }
    } catch (err) {
        alert('Eroare de conexiune la adăugarea cotei TVA.');
    }
}

async function updateProductTva(productId, selectEl) {
    const newTva = selectEl.value;
    selectEl.disabled = true;
    try {
        const resp = await fetch(`/admin/api/product/tva/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cota_tva: newTva })
        });
        const res = await resp.json();
        if (res.success && res.product) {
            const row = selectEl.closest('tr');
            if (row) {
                const netCell = row.querySelector('.admin-net-cell');
                const brutCell = row.querySelector('.admin-brut-cell');
                const varsCell = row.querySelector('.admin-vars-cell');
                if (netCell) netCell.innerText = `${Number(res.product.pret_net).toFixed(2)} RON`;
                if (brutCell) brutCell.innerHTML = `<strong style="color: #065f46;">${Number(res.product.pret_brut).toFixed(2)} RON</strong>`;
                if (varsCell && Array.isArray(res.product.variations)) {
                    varsCell.innerHTML = res.product.variations.map(v => {
                        const codeHtml = v.internal_code
                            ? `<small style="color: #0369a1; font-weight: 700;">[Cod: ${v.internal_code}]</small>`
                            : (v.sku ? `<small style="color: #64748b;">[${v.sku}]</small>` : '');
                        return `<span class="var-badge" style="margin: 2px; display: inline-block;"><strong>${v.size}</strong>: ${Number(v.pret_net).toFixed(2)} &rarr; <strong style="color:#065f46;">${Number(v.pret_brut).toFixed(2)} RON</strong> ${codeHtml}</span>`;
                    }).join('');
                }
            }
        } else {
            alert(res.message || 'Eroare la actualizarea TVA.');
        }
    } catch (err) {
        alert('Eroare de conexiune la actualizarea TVA.');
    } finally {
        selectEl.disabled = false;
    }
}

function collectCurrentVariationRows() {
    const rows = document.querySelectorAll('#variationRowsContainer .var-editor-row');
    const result = [];
    rows.forEach(row => {
        result.push({
            size: row.querySelector('.var-size-input').value.trim(),
            pret_net: row.querySelector('.var-price-input').value.trim(),
            price: row.querySelector('.var-price-input').value.trim(),
            internal_code: row.querySelector('.var-code-input').value.trim(),
            stock: row.querySelector('.var-stock-input').value.trim() || '25',
            sku: row.dataset.sku || ''
        });
    });
    return result;
}

function renderVariationRows(presetVariations = null) {
    const countInput = document.getElementById('varCountInput');
    const container = document.getElementById('variationRowsContainer');
    if (!countInput || !container) return;

    let count = parseInt(countInput.value, 10);
    if (isNaN(count) || count < 1) count = 1;
    if (count > 15) {
        count = 15;
        countInput.value = 15;
    }

    const tvaSelect = document.getElementById('prodCotaTva');
    const tvaPct = tvaSelect ? parseFloat(tvaSelect.value) : 21;
    const existing = presetVariations !== null ? presetVariations : collectCurrentVariationRows();
    let html = `
        <div style="display: grid; grid-template-columns: 1fr 0.95fr 0.9fr 1.15fr 0.65fr; gap: 8px; font-size: 0.76rem; font-weight: 700; color: #065f46; padding: 0 4px;">
            <span>Mărime / Ambalaj *</span>
            <span>Preț NET (RON) *</span>
            <span>Preț BRUT (.50/.00)</span>
            <span>Cod intern (admin)</span>
            <span>Stoc</span>
        </div>
    `;

    for (let i = 0; i < count; i++) {
        const v = existing[i] || {};
        const sizeVal = (v.size !== undefined && v.size !== null) ? String(v.size).replace(/"/g, '&quot;') : '';
        const netRaw = (v.pret_net !== undefined && v.pret_net !== null && v.pret_net !== '') ? v.pret_net : ((v.price !== undefined && v.price !== null && v.price !== '') ? v.price : '');
        const brutPreview = netRaw !== '' ? calcBrutCeilHalf(netRaw, tvaPct).toFixed(2) + ' RON' : '0.00 RON';
        const codeVal = (v.internal_code !== undefined && v.internal_code !== null) ? String(v.internal_code).replace(/"/g, '&quot;') : '';
        const stockVal = (v.stock !== undefined && v.stock !== null && v.stock !== '') ? v.stock : 25;
        const skuVal = (v.sku || '').replace(/"/g, '&quot;');

        html += `
            <div class="var-editor-row" data-sku="${skuVal}" style="display: grid; grid-template-columns: 1fr 0.95fr 0.9fr 1.15fr 0.65fr; gap: 8px; align-items: center;">
                <input type="text" class="var-size-input" required placeholder="ex: ${i === 0 ? '20L' : (i === 1 ? '50L' : '10L')}" value="${sizeVal}"
                       style="padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
                <input type="number" step="0.01" min="0" class="var-price-input" required placeholder="ex: 12.50" value="${netRaw}" oninput="refreshVariationBrutPreviews()"
                       style="padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
                <span class="var-brut-preview" style="padding: 8px 10px; border-radius: 8px; background: #ecfdf5; color: #065f46; font-weight: 700; font-size: 0.85rem; text-align: center; border: 1px solid #a7f3d0;">${brutPreview}</span>
                <input type="text" class="var-code-input" placeholder="ex: FL-RAS-20" value="${codeVal}"
                       style="padding: 8px 10px; border: 1px solid #93c5fd; border-radius: 8px; background: #f8fafc;">
                <input type="number" min="0" class="var-stock-input" value="${stockVal}"
                       style="padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
            </div>
        `;
    }

    container.innerHTML = html;
}

function openAddProductModal() {
    document.getElementById('adminModalTitle').innerHTML = '<i class="fa-solid fa-box"></i> Adaugă Produs Nou';
    document.getElementById('adminProductForm').reset();
    document.getElementById('editProductId').value = '';
    document.getElementById('imagePreviewImg').style.display = 'none';
    document.getElementById('imagePreviewText').style.display = 'block';
    document.getElementById('varCountInput').value = 1;
    const tvaSel = document.getElementById('prodCotaTva');
    if (tvaSel) tvaSel.value = '21';
    renderVariationRows([{ size: '', pret_net: '', internal_code: '', stock: 25 }]);
    updateSubcatOptions();
    autoSuggestTvaByCategory();
    document.getElementById('adminProductModal').classList.add('active');
}

function closeAdminProductModal() {
    document.getElementById('adminProductModal').classList.remove('active');
}

function editProduct(prod) {
    document.getElementById('adminModalTitle').innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Editează Produsul #${prod.id}`;
    document.getElementById('editProductId').value = prod.id;
    document.getElementById('prodName').value = prod.name;
    document.getElementById('prodCategory').value = prod.category;
    updateSubcatOptions();
    document.getElementById('prodSubcategory').value = prod.subcategory || '';
    const tvaSel = document.getElementById('prodCotaTva');
    if (tvaSel) {
        const cota = prod.cota_tva !== undefined ? prod.cota_tva : (prod.category === 'Ingrasaminte' ? 11 : 21);
        tvaSel.value = String(cota);
    }
    document.getElementById('prodPrice').value = prod.pret_net !== undefined ? prod.pret_net : prod.price;
    document.getElementById('prodStock').value = prod.stock || 25;
    document.getElementById('prodDescription').value = prod.description || '';
    document.getElementById('prodFeatured').checked = !!prod.featured;

    const vars = (prod.variations && prod.variations.length > 0)
        ? prod.variations
        : [{ size: 'Standard', pret_net: prod.pret_net !== undefined ? prod.pret_net : prod.price, internal_code: prod.internal_code || '', stock: prod.stock || 25 }];
    document.getElementById('varCountInput').value = vars.length;
    renderVariationRows(vars);

    // Image preview
    const select = document.getElementById('prodImageSelect');
    if (select) {
        select.value = prod.image || '';
        previewSelectedImage(prod.image);
    }

    document.getElementById('adminProductModal').classList.add('active');
}

function previewSelectedImage(url) {
    const img = document.getElementById('imagePreviewImg');
    const text = document.getElementById('imagePreviewText');
    if (url) {
        img.src = url;
        img.style.display = 'inline-block';
        text.style.display = 'none';
    } else {
        img.style.display = 'none';
        text.style.display = 'block';
    }
}

function previewUploadedImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.getElementById('imagePreviewImg');
            const text = document.getElementById('imagePreviewText');
            img.src = e.target.result;
            img.style.display = 'inline-block';
            text.style.display = 'none';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function submitAdminProduct(e) {
    e.preventDefault();
    const form = document.getElementById('adminProductForm');

    // Collect dynamic variation rows
    const rawVars = collectCurrentVariationRows();
    const variations = [];
    for (let i = 0; i < rawVars.length; i++) {
        const size = rawVars[i].size || 'Standard';
        const priceNum = parseFloat(String(rawVars[i].price).replace(',', '.'));
        if (isNaN(priceNum) || priceNum < 0) {
            alert(`Vă rugăm introduceți un preț valid pentru mărimea #${i + 1} (${size}).`);
            return;
        }
        const stockNum = parseInt(rawVars[i].stock, 10) || 25;
        variations.push({
            size: size,
            pret_net: Number(priceNum.toFixed(2)),
            price: Number(priceNum.toFixed(2)),
            stock: stockNum,
            internal_code: rawVars[i].internal_code || '',
            sku: rawVars[i].sku || ''
        });
    }

    if (variations.length === 0) {
        alert('Adăugați cel puțin o mărime / ambalaj cu preț.');
        return;
    }

    document.getElementById('variationsJsonInput').value = JSON.stringify(variations);
    document.getElementById('prodPrice').value = Math.min(...variations.map(v => v.price));
    document.getElementById('prodStock').value = variations.reduce((sum, v) => sum + v.stock, 0);

    const formData = new FormData(form);
    const saveBtn = document.getElementById('saveProdBtn');

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se salvează...';

    try {
        const resp = await fetch('/admin/api/product/save', {
            method: 'POST',
            body: formData
        });
        const res = await resp.json();

        if (res.success) {
            alert(res.message);
            location.reload();
        } else {
            alert(res.message || 'Eroare la salvare.');
        }
    } catch (err) {
        alert('Eroare de conexiune la salvarea produsului.');
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvează Produsul';
    }
}

async function uploadPricesCsv() {
    const fileInput = document.getElementById('pricesCsvFileInput');
    const resultBox = document.getElementById('pricesCsvResultBox');
    const btn = document.getElementById('uploadPricesCsvBtn');

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Selectați mai întâi un fișier CSV!');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se procesează CSV...';
    resultBox.style.display = 'block';
    resultBox.style.background = '#e0f2fe';
    resultBox.style.color = '#0369a1';
    resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se actualizează prețurile după Cod intern produs...';

    try {
        const resp = await fetch('/admin/api/prices/import-csv', {
            method: 'POST',
            body: formData
        });
        const res = await resp.json();

        if (res.success) {
            resultBox.style.background = '#dcfce7';
            resultBox.style.color = '#14532d';
            let html = `<strong><i class="fa-solid fa-circle-check"></i> ${res.message}</strong>`;
            if (res.updated_items && res.updated_items.length > 0) {
                html += `<div style="margin-top: 10px; max-height: 200px; overflow-y: auto; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #bbf7d0;">`;
                res.updated_items.forEach(item => {
                    html += `<div style="padding: 3px 0; border-bottom: 1px solid #f1f5f9;">
                        <code>${item.code}</code> — <strong>${item.product}</strong> (${item.size}):
                        <span style="text-decoration: line-through; color: #94a3b8;">${Number(item.old_price).toFixed(2)}</span> &rarr;
                        <strong style="color: #059669;">${Number(item.new_price).toFixed(2)} RON + TVA</strong>
                    </div>`;
                });
                html += `</div>`;
            }
            if (res.not_found_total > 0) {
                html += `<div style="margin-top: 10px; padding: 8px 12px; background: #fef3c7; color: #92400e; border-radius: 8px;">
                    <strong>Atenție:</strong> ${res.not_found_total} coduri din CSV nu au fost găsite în catalog: <code>${res.not_found_codes.join(', ')}</code>
                </div>`;
            }
            html += `<div style="margin-top: 12px;"><button type="button" class="btn btn-primary" onclick="location.reload()"><i class="fa-solid fa-rotate-right"></i> Reîncarcă Tabelul de Produse</button></div>`;
            resultBox.innerHTML = html;
        } else {
            resultBox.style.background = '#fee2e2';
            resultBox.style.color = '#991b1b';
            resultBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${res.message || 'Eroare la procesarea CSV.'}`;
        }
    } catch (err) {
        resultBox.style.background = '#fee2e2';
        resultBox.style.color = '#991b1b';
        resultBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Eroare de conexiune: ${err.message}`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Încarcă și Actualizează Prețurile';
    }
}

async function deleteProduct(productId) {
    if (!confirm(`Sigur doriți să ștergeți produsul #${productId}?`)) {
        return;
    }

    try {
        const resp = await fetch(`/admin/api/product/delete/${productId}`, {
            method: 'POST'
        });
        const res = await resp.json();

        if (res.success) {
            const row = document.querySelector(`#adminProductsTable tr[data-id="${productId}"]`);
            if (row) row.remove();
            const countEl = document.getElementById('statProdCount');
            if (countEl) countEl.innerText = Math.max(0, (parseInt(countEl.innerText) || 1) - 1);
            alert(res.message);
        } else {
            alert(res.message || 'Eroare la ștergere.');
        }
    } catch (err) {
        alert('Eroare de rețea la ștergerea produsului.');
    }
}

// ---------------- CRM & Settings ---------------- //
function filterCrmTable(query) {
    const q = (query || '').trim().toLowerCase();
    document.querySelectorAll('#crmClientsTable tbody tr').forEach(row => {
        row.style.display = (!q || row.innerText.toLowerCase().includes(q)) ? '' : 'none';
    });
}

async function deleteCrmClient(clientId) {
    if (!confirm(`Sigur doriți să ștergeți definitiv clientul CRM #${clientId} (conform GDPR)?`)) {
        return;
    }
    try {
        const resp = await fetch(`/admin/api/crm/delete/${clientId}`, { method: 'POST' });
        const res = await resp.json();
        if (res.success) {
            const row = document.querySelector(`#crmClientsTable tr[data-crm-id="${clientId}"]`);
            if (row) row.remove();
            alert(res.message);
        } else {
            alert(res.message || 'Eroare la ștergerea clientului CRM.');
        }
    } catch (err) {
        alert('Eroare de conexiune.');
    }
}

async function saveAdminSettings(e) {
    e.preventDefault();
    const btn = document.getElementById('saveSettingsBtn');
    const statusBox = document.getElementById('settingsSaveStatus');

    const payload = {
        order_email: document.getElementById('settingOrderEmail').value.trim(),
        company_name: document.getElementById('settingCompanyName').value.trim(),
        company_phone: document.getElementById('settingCompanyPhone').value.trim(),
        company_cui: document.getElementById('settingCompanyCui').value.trim(),
        company_reg_com: document.getElementById('settingCompanyReg').value.trim(),
        company_address: document.getElementById('settingCompanyAddress').value.trim(),
        company_schedule: document.getElementById('settingCompanySchedule').value.trim(),
        smtp_host: document.getElementById('settingSmtpHost').value.trim(),
        smtp_port: document.getElementById('settingSmtpPort').value.trim(),
        smtp_user: document.getElementById('settingSmtpUser').value.trim(),
        smtp_password: document.getElementById('settingSmtpPassword').value
    };

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se salvează...';

    try {
        const resp = await fetch('/admin/api/settings/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        statusBox.style.display = 'block';
        if (res.success) {
            statusBox.style.background = '#dcfce7';
            statusBox.style.color = '#166534';
            statusBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${res.message}`;
        } else {
            statusBox.style.background = '#fee2e2';
            statusBox.style.color = '#991b1b';
            statusBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${res.message}`;
        }
    } catch (err) {
        statusBox.style.display = 'block';
        statusBox.style.background = '#fee2e2';
        statusBox.style.color = '#991b1b';
        statusBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Eroare de conexiune.`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvează Setările';
    }
}

// ---------------- Category Management (Add / Edit / Delete) ---------------- //
function openAddCategoryModal() {
    document.getElementById('adminCatModalTitle').innerHTML = '<i class="fa-solid fa-folder-plus"></i> Adaugă Categorie Nouă';
    document.getElementById('adminCategoryForm').reset();
    document.getElementById('editCategoryId').value = '';
    document.getElementById('catIcon').value = 'fa-leaf';
    document.getElementById('catUnitLabel').value = 'produse';
    document.getElementById('adminCategoryModal').classList.add('active');
}

function openEditCategoryModal(cat) {
    document.getElementById('adminCatModalTitle').innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Editează Categoria: ${cat.display_name}`;
    document.getElementById('editCategoryId').value = cat.id;
    document.getElementById('catDisplayName').value = cat.display_name || '';
    document.getElementById('catDescription').value = cat.description || '';
    document.getElementById('catIcon').value = cat.icon || 'fa-leaf';
    document.getElementById('catUnitLabel').value = cat.unit_label || 'produse';
    document.getElementById('catSubcategories').value = Array.isArray(cat.subcategories) ? cat.subcategories.join(', ') : '';
    document.getElementById('adminCategoryModal').classList.add('active');
}

function closeAdminCategoryModal() {
    document.getElementById('adminCategoryModal').classList.remove('active');
}

async function submitAdminCategory(e) {
    e.preventDefault();
    const btn = document.getElementById('saveCatBtn');
    const payload = {
        id: document.getElementById('editCategoryId').value || null,
        display_name: document.getElementById('catDisplayName').value.trim(),
        description: document.getElementById('catDescription').value.trim(),
        icon: document.getElementById('catIcon').value,
        unit_label: document.getElementById('catUnitLabel').value.trim() || 'produse',
        subcategories: document.getElementById('catSubcategories').value.trim()
    };

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Se salvează...';

    try {
        const resp = await fetch('/admin/api/category/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            alert(res.message);
            location.reload();
        } else {
            alert(res.message || 'Eroare la salvarea categoriei.');
        }
    } catch (err) {
        alert('Eroare de conexiune la salvarea categoriei.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvează Categoria';
    }
}

async function deleteCategory(catId) {
    if (!confirm('Sigur doriți să ștergeți această categorie?')) {
        return;
    }
    try {
        const resp = await fetch(`/admin/api/category/delete/${catId}`, { method: 'POST' });
        const res = await resp.json();
        if (res.success) {
            alert(res.message);
            location.reload();
        } else {
            alert(res.message || 'Nu s-a putut șterge categoria.');
        }
    } catch (err) {
        alert('Eroare de conexiune.');
    }
}

async function toggleProductActive(productId, checkbox) {
    const isActive = checkbox.checked;
    const row = checkbox.closest('tr');
    const label = checkbox.parentElement ? checkbox.parentElement.querySelector('.active-status-label') : null;

    try {
        const resp = await fetch(`/admin/api/product/toggle-active/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: isActive })
        });
        const res = await resp.json();
        if (res.success) {
            if (row) {
                row.style.opacity = isActive ? '1' : '0.58';
                row.style.background = isActive ? '' : '#f8fafc';
            }
            if (label) {
                label.innerText = isActive ? 'Activ' : 'Inactiv';
                label.style.color = isActive ? '#059669' : '#94a3b8';
            }
        } else {
            checkbox.checked = !isActive;
            alert(res.message || 'Eroare la actualizarea stării produsului.');
        }
    } catch (err) {
        checkbox.checked = !isActive;
        alert('Eroare de conexiune.');
    }
}

async function toggleCategoryActive(catId, checkbox) {
    const isActive = checkbox.checked;
    const row = checkbox.closest('tr');
    const label = checkbox.parentElement ? checkbox.parentElement.querySelector('.active-status-label') : null;

    try {
        const resp = await fetch(`/admin/api/category/toggle-active/${catId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: isActive })
        });
        const res = await resp.json();
        if (res.success) {
            if (row) {
                row.style.opacity = isActive ? '1' : '0.58';
                row.style.background = isActive ? '' : '#f8fafc';
            }
            if (label) {
                label.innerText = isActive ? 'Activ' : 'Inactiv';
                label.style.color = isActive ? '#059669' : '#94a3b8';
            }
        } else {
            checkbox.checked = !isActive;
            alert(res.message || 'Eroare la actualizarea stării categoriei.');
        }
    } catch (err) {
        checkbox.checked = !isActive;
        alert('Eroare de conexiune.');
    }
}

// ---------------- Order Status Workflow (Comandă nouă -> În prelucrare -> Finalizată) ---------------- //
let currentOpenOrderId = null;

function styleOrderStatusSelect(selectEl, status) {
    if (!selectEl) return;
    if (status === 'Comandă nouă') {
        selectEl.style.borderColor = '#3b82f6';
        selectEl.style.background = '#dbeafe';
        selectEl.style.color = '#1e40af';
    } else if (status === 'În prelucrare') {
        selectEl.style.borderColor = '#f59e0b';
        selectEl.style.background = '#fef3c7';
        selectEl.style.color = '#92400e';
    } else {
        selectEl.style.borderColor = '#10b981';
        selectEl.style.background = '#dcfce7';
        selectEl.style.color = '#166534';
    }
}

async function updateOrderStatus(orderId, newStatus, selectEl = null) {
    const rowSelect = selectEl || document.querySelector(`.order-status-select[data-order-id="${orderId}"]`);
    const modalSelect = document.getElementById('orderModalStatusSelect');
    const cachedOrder = window.ADMIN_ORDERS_MAP ? window.ADMIN_ORDERS_MAP[orderId] : null;
    const prevStatus = cachedOrder ? (cachedOrder.status || 'Comandă nouă') : 'În prelucrare';

    // Client-side gate before finalizing without shipping cost
    if (newStatus === 'Finalizată' && cachedOrder && (cachedOrder.cost_transport_brut === null || cachedOrder.cost_transport_brut === undefined)) {
        if (rowSelect) {
            rowSelect.value = prevStatus;
            styleOrderStatusSelect(rowSelect, prevStatus);
        }
        if (modalSelect && currentOpenOrderId === orderId) {
            modalSelect.value = prevStatus;
            styleOrderStatusSelect(modalSelect, prevStatus);
        }
        openOrderDetailModal(cachedOrder, true);
        return;
    }

    try {
        const resp = await fetch(`/admin/api/order/status/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const res = await resp.json();
        if (res.success) {
            if (cachedOrder) cachedOrder.status = newStatus;
            if (res.order && window.ADMIN_ORDERS_MAP) window.ADMIN_ORDERS_MAP[orderId] = res.order;
            if (rowSelect) {
                rowSelect.value = newStatus;
                styleOrderStatusSelect(rowSelect, newStatus);
            }
            if (modalSelect && currentOpenOrderId === orderId) {
                modalSelect.value = newStatus;
                styleOrderStatusSelect(modalSelect, newStatus);
            }
            const finalBtn = document.getElementById('markOrderFinalBtn');
            if (finalBtn && currentOpenOrderId === orderId) {
                finalBtn.style.display = (newStatus === 'Finalizată') ? 'none' : 'inline-flex';
            }
        } else if (res.require_shipping) {
            if (rowSelect) {
                rowSelect.value = prevStatus;
                styleOrderStatusSelect(rowSelect, prevStatus);
            }
            if (modalSelect && currentOpenOrderId === orderId) {
                modalSelect.value = prevStatus;
                styleOrderStatusSelect(modalSelect, prevStatus);
            }
            if (cachedOrder) openOrderDetailModal(cachedOrder, true);
            else alert(res.message);
        } else {
            alert(res.message || 'Eroare la schimbarea statusului.');
        }
    } catch (err) {
        alert('Eroare de conexiune la actualizarea statusului comenzii.');
    }
}

async function saveOrderShipping(orderId) {
    const input = document.getElementById('orderShippingInput');
    const feedback = document.getElementById('orderShippingFeedback');
    const btn = document.getElementById('saveOrderShippingBtn');
    if (!input) return;

    const rawVal = input.value.trim();
    if (rawVal === '') {
        if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#b91c1c';
            feedback.innerText = 'Introduceți costul de transport (0 pentru transport gratuit / ridicare personală).';
        }
        input.focus();
        return;
    }

    if (btn) btn.disabled = true;
    try {
        const resp = await fetch(`/admin/api/order/shipping/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cost_transport_brut: rawVal, cota_tva_transport: 21 })
        });
        const res = await resp.json();
        if (res.success && res.order) {
            if (window.ADMIN_ORDERS_MAP) window.ADMIN_ORDERS_MAP[orderId] = res.order;
            const row = document.querySelector(`tr[data-order-id="${orderId}"]`);
            if (row) {
                const totalCell = row.querySelector('.order-total-cell');
                if (totalCell) {
                    totalCell.innerHTML = `<strong style="color: #059669;">${Number(res.order.total).toFixed(2)} RON (TVA inclus)</strong>`;
                }
            }
            openOrderDetailModal(res.order, false);
            const fb = document.getElementById('orderShippingFeedback');
            if (fb) {
                fb.style.display = 'block';
                fb.style.color = '#15803d';
                fb.innerHTML = '<i class="fa-solid fa-circle-check"></i> Costul de transport a fost salvat și totalul de facturat recalculat.';
            }
        } else {
            if (feedback) {
                feedback.style.display = 'block';
                feedback.style.color = '#b91c1c';
                feedback.innerText = res.message || 'Eroare la salvarea costului de transport.';
            }
        }
    } catch (err) {
        alert('Eroare de conexiune la salvarea costului de transport.');
    } finally {
        if (btn) btn.disabled = false;
    }
}

function openOrderDetailModal(order, highlightMissingShipping = false) {
    if (!order) return;
    currentOpenOrderId = order.id;
    const rowSelect = document.querySelector(`.order-status-select[data-order-id="${order.id}"]`);
    let currentStatus = rowSelect ? rowSelect.value : (order.status || 'Comandă nouă');

    document.getElementById('orderModalTitle').innerHTML = `<i class="fa-solid fa-receipt"></i> Comandă #${order.id} — ${order.date || ''}`;

    const cust = order.customer || {};
    let fallbackTotalNet = 0;
    let fallbackTotalTva = 0;
    let fallbackTotalBrut = 0;

    const itemsHtml = (order.items || []).map(it => {
        const qty = Number(it.quantity || 1);
        const cota = it.cota_tva !== undefined ? Number(it.cota_tva) : 21;
        const unitBrut = Number(it.pret_brut_unitar !== undefined ? it.pret_brut_unitar : (it.price || 0));
        const unitNet = it.pret_net_recalculat !== undefined
            ? Number(it.pret_net_recalculat)
            : Number((unitBrut / (1 + cota / 100)).toFixed(2));
        const valBrut = it.valoare_bruta !== undefined ? Number(it.valoare_bruta) : Number((unitBrut * qty).toFixed(2));
        const valNet = it.valoare_neta !== undefined ? Number(it.valoare_neta) : Number((unitNet * qty).toFixed(2));
        const valTva = it.valoare_tva !== undefined ? Number(it.valoare_tva) : Number((valBrut - valNet).toFixed(2));

        fallbackTotalNet += valNet;
        fallbackTotalTva += valTva;
        fallbackTotalBrut += valBrut;

        return `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px 6px;"><strong>${it.name}</strong></td>
                <td style="padding: 8px 6px; text-align: center;">${qty} buc</td>
                <td style="padding: 8px 6px; text-align: center;"><span style="background:#ecfdf5;color:#065f46;padding:2px 7px;border-radius:6px;font-weight:700;font-size:0.8rem;">${cota}%</span></td>
                <td style="padding: 8px 6px; text-align: right; color:#475569;">${unitNet.toFixed(2)} RON</td>
                <td style="padding: 8px 6px; text-align: right; font-weight:600;">${unitBrut.toFixed(2)} RON</td>
                <td style="padding: 8px 6px; text-align: right; color:#475569;">${valNet.toFixed(2)} RON</td>
                <td style="padding: 8px 6px; text-align: right; color:#0369a1;">${valTva.toFixed(2)} RON</td>
                <td style="padding: 8px 6px; text-align: right; font-weight: 700; color:#064e3b;">${valBrut.toFixed(2)} RON</td>
            </tr>
        `;
    }).join('');

    const prodNet = order.total_net !== undefined ? Number(order.total_net) : fallbackTotalNet;
    const prodTva = order.total_tva !== undefined ? Number(order.total_tva) : fallbackTotalTva;
    const prodBrut = order.subtotal_brut !== undefined ? Number(order.subtotal_brut) : fallbackTotalBrut;

    const hasShipping = order.cost_transport_brut !== null && order.cost_transport_brut !== undefined;
    const shipCota = order.cota_tva_transport !== undefined ? Number(order.cota_tva_transport) : 21;
    const shipBrut = hasShipping ? Number(order.cost_transport_brut) : 0;
    const shipNet = hasShipping && order.cost_transport_net !== null && order.cost_transport_net !== undefined
        ? Number(order.cost_transport_net)
        : (hasShipping ? Number((shipBrut / (1 + shipCota / 100)).toFixed(2)) : 0);
    const shipTva = hasShipping && order.cost_transport_tva !== null && order.cost_transport_tva !== undefined
        ? Number(order.cost_transport_tva)
        : (hasShipping ? Number((shipBrut - shipNet).toFixed(2)) : 0);

    const factNet = order.total_facturat_net !== undefined ? Number(order.total_facturat_net) : (prodNet + shipNet);
    const factTva = order.total_facturat_tva !== undefined ? Number(order.total_facturat_tva) : (prodTva + shipTva);
    const factBrut = order.total_facturat_brut !== undefined ? Number(order.total_facturat_brut) : (prodBrut + shipBrut);

    const activeBreakdown = (order.tva_breakdown_facturat && order.tva_breakdown_facturat.length > 0)
        ? order.tva_breakdown_facturat
        : (order.tva_breakdown || []);

    const breakdownHtml = activeBreakdown.map(b => `
        <div style="display:flex;justify-content:space-between;font-size:0.83rem;color:#475569;padding:2px 0;">
            <span>&bull; TVA ${b.cota_tva}% (bază netă ${Number(b.valoare_neta).toFixed(2)} RON):</span>
            <strong>${Number(b.valoare_tva).toFixed(2)} RON</strong>
        </div>
    `).join('');

    const shippingWarningHtml = highlightMissingShipping ? `
        <div style="background:#fff7ed;border:1.5px solid #fb923c;color:#9a3412;padding:10px 14px;border-radius:10px;font-size:0.86rem;font-weight:700;margin-bottom:10px;">
            <i class="fa-solid fa-triangle-exclamation"></i> Introduceți costul de transport (TVA inclus) stabilit cu curierul înainte de a marca comanda ca Finalizată.
        </div>
    ` : '';

    document.getElementById('orderModalBody').innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px; background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div>
                <div style="font-size: 0.78rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">Date Client</div>
                <div><strong>${cust.name || '-'}</strong></div>
                <div><i class="fa-solid fa-phone" style="color: #059669;"></i> ${cust.phone || '-'}</div>
                <div><i class="fa-solid fa-envelope" style="color: #0284c7;"></i> ${cust.email || '-'}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">Livrare &amp; Plată</div>
                <div>${cust.county || ''}, ${cust.city || ''}</div>
                <div>${cust.address || '-'}</div>
                <div style="margin-top: 4px;">Plată: <strong>${order.payment_method || '-'}</strong></div>
            </div>
        </div>
        <div style="overflow-x:auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-bottom: 16px;">
                <thead>
                    <tr style="background: #f1f5f9; text-align: left;">
                        <th style="padding: 8px 6px;">Produs &amp; ambalaj</th>
                        <th style="padding: 8px 6px; text-align: center;">Cant.</th>
                        <th style="padding: 8px 6px; text-align: center;">TVA %</th>
                        <th style="padding: 8px 6px; text-align: right;">Preț net</th>
                        <th style="padding: 8px 6px; text-align: right;">Preț brut</th>
                        <th style="padding: 8px 6px; text-align: right;">Total net</th>
                        <th style="padding: 8px 6px; text-align: right;">TVA</th>
                        <th style="padding: 8px 6px; text-align: right;">Total brut</th>
                    </tr>
                </thead>
                <tbody>${itemsHtml}</tbody>
            </table>
        </div>

        <!-- Editable Courier Shipping Cost (mandatory before Finalizată) -->
        <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
            ${shippingWarningHtml}
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <label for="orderShippingInput" style="font-weight:700;color:#065f46;font-size:0.9rem;display:block;">
                        <i class="fa-solid fa-truck"></i> Cost transport (RON, TVA ${shipCota}% inclus)
                    </label>
                    <small style="color:#475569;">Introduceți <strong>0</strong> pentru transport gratuit sau ridicare personală.</small>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <input type="number" step="0.01" min="0" id="orderShippingInput"
                           value="${hasShipping ? shipBrut.toFixed(2) : ''}"
                           placeholder="ex: 25.00"
                           style="width:120px;padding:8px 10px;border:1.5px solid ${highlightMissingShipping ? '#ea580c' : '#059669'};border-radius:8px;font-weight:700;text-align:right;background:#fff;">
                    <button type="button" id="saveOrderShippingBtn" class="btn-action" onclick="saveOrderShipping(${order.id})"
                            style="background:#059669;color:#fff;padding:9px 14px;border-radius:8px;">
                        <i class="fa-solid fa-floppy-disk"></i> Salvează transport
                    </button>
                </div>
            </div>
            <div id="orderShippingFeedback" style="display:none;margin-top:8px;font-size:0.84rem;font-weight:600;"></div>
        </div>

        <!-- Full Invoice Summary (Subtotal produse + Cost transport = Total general de facturat) -->
        <div style="display:grid;grid-template-columns:1fr 1.15fr;gap:14px;">
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;font-size:0.86rem;">
                <div style="font-weight:800;color:#0f172a;margin-bottom:8px;">Defalcare Produse &amp; Transport</div>
                <div style="padding:4px 0;border-bottom:1px dashed #cbd5e1;">
                    <strong>Subtotal produse:</strong><br>
                    Net: ${prodNet.toFixed(2)} RON | TVA: ${prodTva.toFixed(2)} RON | <strong>Brut: ${prodBrut.toFixed(2)} RON</strong>
                </div>
                <div style="padding:6px 0 0 0;">
                    <strong>Cost transport (${shipCota}% TVA):</strong><br>
                    ${hasShipping
                        ? `Net: ${shipNet.toFixed(2)} RON | TVA ${shipCota}%: ${shipTva.toFixed(2)} RON | <strong>Brut: ${shipBrut.toFixed(2)} RON</strong>`
                        : '<span style="color:#9a3412;font-weight:600;">Necompletat (se comunică telefonic)</span>'}
                </div>
            </div>
            <div style="background: #f8fbf9; border: 1.5px solid #a7f3d0; border-radius: 12px; padding: 14px 16px;">
                <div style="font-weight:800;color:#064e3b;font-size:0.9rem;margin-bottom:6px;">Total general de facturat</div>
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;padding:3px 0;">
                    <span>Total Net (fără TVA):</span>
                    <strong>${factNet.toFixed(2)} RON</strong>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;padding:3px 0;color:#0369a1;">
                    <span>Total TVA (produse + transport):</span>
                    <strong>${factTva.toFixed(2)} RON</strong>
                </div>
                ${breakdownHtml}
                <div style="display:flex;justify-content:space-between;font-size:1.08rem;font-weight:800;color:#064e3b;border-top:1px solid #a7f3d0;margin-top:8px;padding-top:8px;">
                    <span>Total de facturat (TVA inclus):</span>
                    <span>${factBrut.toFixed(2)} RON</span>
                </div>
            </div>
        </div>
    `;

    const modalSelect = document.getElementById('orderModalStatusSelect');
    if (modalSelect) {
        modalSelect.value = currentStatus;
        styleOrderStatusSelect(modalSelect, currentStatus);
    }
    const finalBtn = document.getElementById('markOrderFinalBtn');
    if (finalBtn) {
        finalBtn.style.display = (currentStatus === 'Finalizată') ? 'none' : 'inline-flex';
    }

    document.getElementById('adminOrderModal').classList.add('active');

    if (highlightMissingShipping) {
        setTimeout(() => {
            const inp = document.getElementById('orderShippingInput');
            if (inp) inp.focus();
        }, 80);
    } else if (currentStatus === 'Comandă nouă') {
        updateOrderStatus(order.id, 'În prelucrare', rowSelect);
    }
}

function changeCurrentModalOrderStatus(newStatus) {
    if (!currentOpenOrderId) return;
    updateOrderStatus(currentOpenOrderId, newStatus);
}

function closeOrderDetailModal() {
    document.getElementById('adminOrderModal').classList.remove('active');
    currentOpenOrderId = null;
}
