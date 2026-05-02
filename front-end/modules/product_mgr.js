// Correctly decode the JWT to get your ID
function currentUserId() {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) return '';

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        // Django JWT usually uses 'user_id'
        return payload.user_id || payload.id || ''; 
    } catch (e) {
        return '';
    }
}

// Ensure the fetch URL matches your urls.py exactly
async function loadVendorProducts() {
    const list = document.getElementById('vendor-products-list');
    const vendorId = currentUserId();

    if (!vendorId) {
        list.innerHTML = '<div class="alert alert-warning">Connectez-vous.</div>';
        return;
    }

    // Note the trailing slash after 'vendor/' to match your urls.py
    const url = `${CONFIG.API_PRODUCTS_URL}/vendor/?vendor_id=${vendorId}`;
    
    const response = await fetch(url, {
        headers: { ...authHeader() }
    });
    
    const products = await response.json();
    // ... rest of your rendering logic
}

function productImageUrl(path) {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    return `${CONFIG.API_PRODUCTS_URL}${path}`;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

async function fetchPublicUsersByIds(ids = []) {
    const unique = Array.from(new Set(ids.map((x) => String(x)).filter(Boolean)));
    if (!unique.length) return {};

    try {
        const response = await fetch(`${CONFIG.API_USERS_URL}/api/public-users/?ids=${unique.join(',')}`);
        if (!response.ok) return {};
        const data = await response.json();
        if (!Array.isArray(data)) return {};
        return Object.fromEntries(data.map((u) => [String(u.id), u]));
    } catch (_) {
        return {};
    }
}

async function loadProducts() {
    const grid = document.getElementById('products-grid');
    const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/`);
    const products = await response.json();

    const usersById = await fetchPublicUsersByIds(products.map((p) => p.vendor_id));

    grid.innerHTML = products.map(p => `
        <div class="col-md-4">
            <div class="product-card">
                <div class="img-container">
                    <img src="${productImageUrl(p.image)}" class="product-img" alt="${escapeHtml(p.name)}">
                </div>
                <div class="p-4">
                    <h5 class="product-title">${escapeHtml(p.name)}</h5>
                    <div class="mb-2">
                        <span class="badge rounded-pill bg-light text-primary border">
                            <i class="bi bi-person-badge me-1"></i>
                            ${escapeHtml((usersById[String(p.vendor_id)] || {}).username || `#${p.vendor_id}`)}
                        </span>
                    </div>
                    <div class="price-tag">${p.price} DA</div>
                    <a href="product_detail.html?id=${p.id}" class="btn btn-outline-custom w-100 mt-3">Voir</a>
                </div>
            </div>
        </div>
    `).join('');
}

async function loadVendorProducts() {
    const list = document.getElementById('vendor-products-list');
    const vendorId = currentUserId();

    if (!vendorId) {
        list.innerHTML = '<div class="col-12"><div class="alert alert-warning">Connectez-vous comme vendeur pour voir vos produits.</div></div>';
        return;
    }

    const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/vendor/?vendor_id=${vendorId}`, {
        headers: { ...authHeader() }
    });
    const products = await response.json();

    if (!response.ok) {
        list.innerHTML = `<div class="col-12"><div class="alert alert-danger">${escapeHtml(products.error || 'Impossible de charger vos produits.')}</div></div>`;
        return;
    }

    if (!products.length) {
        list.innerHTML = '<div class="col-12"><div class="alert alert-info">Aucun produit pour le moment. Ajoutez votre premier article.</div></div>';
        return;
    }

    list.innerHTML = products.map(p => `
        <div class="col-md-4">
            <div class="manage-card">
                <img src="${productImageUrl(p.image)}" class="manage-img" alt="${escapeHtml(p.name)}">
                <div class="p-3">
                    <h5>${escapeHtml(p.name)}</h5>
                    <p class="text-muted mb-1">Stock: ${p.stock}</p>
                    <p class="fw-bold mb-3">${p.price} DA</p>
                    <div class="btn-action-group">
                        <a href="product_detail.html?id=${p.id}" class="btn-manage btn-manage-view" title="Détails"><i class="bi bi-eye"></i></a>
                        <a href="edit_product.html?id=${p.id}" class="btn-manage btn-manage-edit" title="Modifier"><i class="bi bi-pencil"></i></a>
                        <button type="button" onclick="deleteProduct(${p.id})" class="btn-manage btn-manage-delete" title="Supprimer"><i class="bi bi-trash"></i></button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function deleteProduct(id) {
    if (!confirm('Supprimer ce produit ?')) return;

    const vendorId = currentUserId();
    const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/${id}/?vendor_id=${vendorId}`, {
        method: 'DELETE',
        headers: { ...authHeader() }
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        alert(data.error || 'Suppression impossible.');
        return;
    }

    loadVendorProducts();
}

async function loadProductDetail() {
    const container = document.getElementById('product-detail-container');
    if (!container) return;

    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) {
        container.innerHTML = '<div class="alert alert-danger">Product id manquant.</div>';
        return;
    }

    container.innerHTML = '<div class="alert alert-info mt-4">Chargement du produit...</div>';

    let p = null;
    try {
        const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/${id}/`);
        const data = await response.json();

        if (response.ok && data && data.id) {
            p = data;
        }
    } catch (error) {
        p = null;
    }

    if (!p) {
        try {
            const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/`);
            const products = await response.json();
            p = products.find(product => String(product.id) === String(id));
        } catch (error) {
            p = null;
        }
    }

    if (!p) {
        container.innerHTML = `
            <div class="alert alert-warning mt-4">
                Produit introuvable. Vérifiez que le service Products est lancé sur ${CONFIG.API_PRODUCTS_URL}.
            </div>
        `;
        return;
    }

    const usersById = await fetchPublicUsersByIds([p.vendor_id]);
    const vendorName = (usersById[String(p.vendor_id)] || {}).username || `#${p.vendor_id}`;

    const isAuth = Boolean(getAccessToken && getAccessToken());
    const role = localStorage.getItem('user_role') || '';
    const canBuy = isAuth && role === 'acheteur';

    container.innerHTML = `
      <div class="detail-card p-4 p-lg-5 mt-4">
        <div class="row g-5 align-items-center">
          <div class="col-md-5">
            ${
              p.image
                ? `<img class="img-fluid rounded-4 border bg-white" src="${productImageUrl(p.image)}" alt="${escapeHtml(p.name)}">`
                : `<div class="border rounded-4 bg-light d-flex align-items-center justify-content-center" style="min-height:280px;"><span class="text-muted">Aucune image</span></div>`
            }
          </div>
          <div class="col-md-7">
            <h2 class="fw-bold mb-3">${escapeHtml(p.name)}</h2>
            <div class="text-muted mb-4">${escapeHtml(p.description)}</div>
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="badge bg-primary">Stock: ${p.stock}</span>
              <span class="badge bg-dark">${escapeHtml(p.category)}</span>
            </div>
            <div class="fs-2 fw-bold text-danger mb-4">${p.price} DA</div>
            <div class="p-3 bg-light border rounded-4 mb-4">
              <div class="text-muted small fw-bold">DISTRIBUTEUR</div>
              <div class="fw-semibold"><i class="bi bi-patch-check-fill text-primary me-2"></i>${escapeHtml(vendorName)}</div>
            </div>
            <div class="row g-2 mb-4">
              ${[p.image2, p.image3, p.image4].filter(Boolean).map(image => `
                <div class="col-4">
                  <img class="img-fluid rounded-3 border bg-white" src="${productImageUrl(image)}" alt="${escapeHtml(p.name)}">
                </div>
              `).join('')}
            </div>
            <div class="d-flex flex-wrap gap-2">
              ${
                canBuy
                  ? `<a class="btn btn-primary px-4" href="../orders/create_order.html?product_id=${p.id}">Commander maintenant</a>`
                  : ''
              }
              <a class="btn btn-outline-secondary px-4" href="Marketplace.html">Retour</a>
            </div>
          </div>
        </div>
      </div>
    `;
}

async function submitProductForm(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const error = document.getElementById('product-form-error');
    const submit = form.querySelector('button[type="submit"]');
    const vendorId = currentUserId();

    if (!vendorId) {
        error.textContent = 'Connectez-vous comme vendeur avant d’ajouter un produit.';
        error.style.display = 'block';
        return;
    }

    const data = new FormData(form);
    data.set('vendor_id', vendorId);
    error.style.display = 'none';
    submit.disabled = true;

    try {
        const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/create/`, {
            method: 'POST',
            headers: { ...authHeader() },
            body: data,
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || JSON.stringify(result));
        }

        window.location.href = 'my-products.html';
    } catch (err) {
        error.textContent = err.message || 'Erreur lors de l’ajout du produit.';
        error.style.display = 'block';
    } finally {
        submit.disabled = false;
    }
}

async function loadEditProductForm() {
    const form = document.getElementById('editProductForm');
    if (!form) return;

    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) {
        document.getElementById('product-form-error').textContent = 'Produit manquant.';
        document.getElementById('product-form-error').style.display = 'block';
        return;
    }

    const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/${id}/`);
    const product = await response.json();
    if (!response.ok) {
        document.getElementById('product-form-error').textContent = product.error || 'Produit introuvable.';
        document.getElementById('product-form-error').style.display = 'block';
        return;
    }

    form.dataset.productId = id;
    form.name.value = product.name || '';
    form.category.value = product.category || 'other';
    form.price.value = product.price || '';
    form.stock.value = product.stock || '';
    form.description.value = product.description || '';
}

async function submitEditProductForm(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const error = document.getElementById('product-form-error');
    const submit = form.querySelector('button[type="submit"]');
    const vendorId = currentUserId();
    const id = form.dataset.productId;

    if (!id || !vendorId) {
        error.textContent = 'Connectez-vous comme vendeur avant de modifier ce produit.';
        error.style.display = 'block';
        return;
    }

    const data = new FormData(form);
    for (const field of ['image', 'image2', 'image3', 'image4']) {
        if (!data.get(field) || !data.get(field).name) data.delete(field);
    }

    error.style.display = 'none';
    submit.disabled = true;

    try {
        const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/${id}/?vendor_id=${vendorId}`, {
            method: 'PATCH',
            headers: { ...authHeader() },
            body: data,
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || JSON.stringify(result));
        }

        window.location.href = 'my-products.html';
    } catch (err) {
        error.textContent = err.message || 'Erreur lors de la modification.';
        error.style.display = 'block';
    } finally {
        submit.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('products-grid')) loadProducts();
    if (document.getElementById('vendor-products-list')) loadVendorProducts();
    if (document.getElementById('product-detail-container')) loadProductDetail();

    const productForm = document.getElementById('productForm');
    if (productForm) productForm.addEventListener('submit', submitProductForm);

    const editProductForm = document.getElementById('editProductForm');
    if (editProductForm) {
        loadEditProductForm();
        editProductForm.addEventListener('submit', submitEditProductForm);
    }
});
