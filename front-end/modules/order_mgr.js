function orderUserId() {
  return window.currentUserId ? window.currentUserId() : '';
}

function escapeOrderHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

const STATUS_LABELS = {
  pending: 'En attente',
  accepted: 'Approuvee',
  rejected: 'Refusee',
  preparing: 'En preparation',
  shipped: 'Expediee',
  delivered: 'Livree',
  cancelled: 'Annulee',
};

async function fetchProducts() {
  const response = await fetch(`${CONFIG.API_PRODUCTS_URL}/api/products/`);
  if (!response.ok) return [];
  return response.json();
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

async function fetchOrders() {
  const response = await fetch(`${CONFIG.API_ORDERS_URL}/api/orders/`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error('Erreur de connexion au service Orders.');
  return response.json();
}

function orderItemsHtml(order, productsById, usersById) {
  return (order.items || []).map((item) => {
    const product = productsById[String(item.product_id)];
    const name = product ? product.name : `Produit #${item.product_id}`;
    const vendorId = product ? product.vendor_id : '';
    const vendorName = vendorId ? ((usersById[String(vendorId)] || {}).username || `#${vendorId}`) : '';

    return `
      <li class="mb-2">
        <div class="fw-semibold">${escapeOrderHtml(name)}</div>
        <div class="small text-muted">Quantité : ${item.quantity} pièce(s)</div>
        ${vendorName ? `<div class="small text-muted">Vendeur : ${escapeOrderHtml(vendorName)}</div>` : ''}
      </li>
    `;
  }).join('');
}

function buyerOrderCard(order, productsById, usersById) {
  const label = STATUS_LABELS[order.status] || order.status;
  return `
    <div class="order-card mb-3">
      <div class="d-flex flex-wrap justify-content-between gap-2">
        <h4 class="order-id">Commande #${order.id}</h4>
        <span class="badge rounded-pill text-bg-${order.status === 'accepted' ? 'success' : order.status === 'rejected' ? 'danger' : 'secondary'}">${label}</span>
      </div>
      <div class="row g-2 mt-2">
        <div class="col-md-4"><strong>Date:</strong> ${new Date(order.created_at).toLocaleDateString()}</div>
        <div class="col-md-4"><strong>Ville:</strong> ${escapeOrderHtml(order.city)}</div>
        <div class="col-md-4"><strong>Paiement:</strong> ${escapeOrderHtml(order.payment_method)}</div>
      </div>
      <div class="mt-3">
        <strong>Produits:</strong>
        <ul class="mt-2 mb-0">${orderItemsHtml(order, productsById, usersById)}</ul>
      </div>
      ${order.vendor_note ? `<div class="alert alert-info mt-3 mb-0">${escapeOrderHtml(order.vendor_note)}</div>` : ''}
    </div>
  `;
}

function vendorOrderCard(order, productsById, usersById, vendorProductIds) {
  const label = STATUS_LABELS[order.status] || order.status;
  const date = new Date(order.created_at).toLocaleString();
  const vendorItems = (order.items || []).filter((item) => vendorProductIds.has(String(item.product_id)));
  const productTags = vendorItems.map((item) => {
    const product = productsById[String(item.product_id)];
    const name = product ? product.name : `Produit #${item.product_id}`;
    return `<div class="product-tag">${item.quantity}x ${escapeOrderHtml(name)}</div>`;
  }).join('');
  const buyerName = (usersById[String(order.buyer_id)] || {}).username || `#${order.buyer_id}`;

  return `
    <div class="order-card mb-5" data-order-status="${escapeOrderHtml(order.status)}">
      <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <span class="text-muted">ID COMMANDE</span>
          <h3 class="fw-bold mb-0">#${order.id}</h3>
        </div>
        <div class="text-end">
          <span class="status-pill st-${order.status}">${label}</span>
          <div class="small text-muted mt-2">${date}</div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-7">
          <span class="section-label">Details Logistiques</span>
          <div class="info-grid">
            <div class="info-item">
              <label><i class="bi bi-person me-1"></i> Acheteur</label>
              <span>${escapeOrderHtml(buyerName)}</span>
            </div>
            <div class="info-item">
              <label><i class="bi bi-telephone me-1"></i> Contact</label>
              <span>${escapeOrderHtml(order.phone)}</span>
            </div>
            <div class="info-item">
              <label><i class="bi bi-geo-alt me-1"></i> Ville / Destination</label>
              <span>${escapeOrderHtml(order.city)}</span>
            </div>
            <div class="info-item">
              <label><i class="bi bi-wallet2 me-1"></i> Paiement</label>
              <span>${escapeOrderHtml(order.payment_method)}</span>
            </div>
          </div>

          <div class="mb-4">
            <label class="text-muted small fw-bold mb-1">ADRESSE PRECISE</label>
            <p class="mb-2 fw-semibold">${escapeOrderHtml(order.delivery_address)}</p>
            ${
              order.delivery_note
                ? `<div class="p-3 border-start border-primary border-4 bg-light rounded-3 small">
                    <i class="bi bi-chat-left-dots me-2"></i><strong>Note client :</strong> ${escapeOrderHtml(order.delivery_note)}
                  </div>`
                : ''
            }
          </div>

          <span class="section-label">Articles de votre catalogue</span>
          <div class="mb-4">${productTags || '<span class="text-muted">Aucun article vendeur dans cette commande.</span>'}</div>
        </div>

        <div class="col-lg-5">
          <div class="form-update">
            <span class="section-label text-dark">Mise a jour logistique</span>
            <div class="mb-3">
              <label class="form-label small fw-bold">Date de livraison prevue</label>
              <input type="date" id="delivery-${order.id}" value="${order.estimated_delivery || ''}" class="form-control">
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold">Votre note interne / Message client</label>
              <textarea id="note-${order.id}" class="form-control" rows="2" placeholder="Ex: Colis pret pour expedition...">${escapeOrderHtml(order.vendor_note || '')}</textarea>
            </div>

            <button type="button" class="btn btn-primary w-100 fw-bold rounded-3" onclick="updateOrderLogistics(${order.id})">
              Enregistrer les infos
            </button>

            <div class="mt-4 pt-3 border-top">
              <label class="section-label mb-3">Changer l'etat</label>
              <div class="d-flex flex-wrap gap-2">
                <button type="button" onclick="setOrderStatus(${order.id}, 'accepted')" class="btn btn-action btn-success">Accepter</button>
                <button type="button" onclick="setOrderStatus(${order.id}, 'preparing')" class="btn btn-action btn-primary">Preparation</button>
                <button type="button" onclick="setOrderStatus(${order.id}, 'shipped')" class="btn btn-action btn-info text-white">Expediee</button>
                <button type="button" onclick="setOrderStatus(${order.id}, 'delivered')" class="btn btn-action btn-success">Livree</button>
                <button type="button" onclick="setOrderStatus(${order.id}, 'rejected')" class="btn btn-action btn-outline-danger">Refuser</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

async function loadBuyerOrders() {
  const container = document.getElementById('orders-list-container');
  const userId = orderUserId();
  const [orders, products] = await Promise.all([fetchOrders(), fetchProducts()]);
  const productsById = Object.fromEntries(products.map((p) => [String(p.id), p]));
  const usersById = await fetchPublicUsersByIds([
    ...orders.map((o) => o.buyer_id),
    ...products.map((p) => p.vendor_id),
  ]);
  const filtered = orders.filter((order) => String(order.buyer_id) === String(userId));

  if (!filtered.length) {
    container.innerHTML = '<div class="alert alert-info">Aucune commande pour le moment.</div>';
    return;
  }

  container.innerHTML = filtered.map((order) => buyerOrderCard(order, productsById, usersById)).join('');
}

async function loadVendorOrders() {
  const container = document.getElementById('orders-list-container');
  const userId = orderUserId();

  if (!userId) {
    container.innerHTML = '<div class="alert alert-warning">Connectez-vous comme vendeur pour voir les commandes recues.</div>';
    return;
  }

  const [orders, products] = await Promise.all([fetchOrders(), fetchProducts()]);
  const vendorProducts = products.filter((product) => String(product.vendor_id) === String(userId));
  const vendorProductIds = new Set(vendorProducts.map((product) => String(product.id)));
  const productsById = Object.fromEntries(products.map((p) => [String(p.id), p]));
  const usersById = await fetchPublicUsersByIds(orders.map((o) => o.buyer_id));
  const filtered = orders.filter((order) => (order.items || []).some((item) => vendorProductIds.has(String(item.product_id))));

  if (!filtered.length) {
    container.innerHTML = `
      <div class="text-center py-5 bg-light rounded-5">
        <i class="bi bi-box2 display-1 text-muted opacity-25"></i>
        <h3 class="mt-3 fw-bold text-muted">Aucune commande pour le moment</h3>
        <p class="text-muted">Des qu'un client commande vos produits, ils apparaitront ici.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map((order) => vendorOrderCard(order, productsById, usersById, vendorProductIds)).join('');
}

async function loadAdminOrders() {
  const container = document.getElementById('orders-list-container');
  const [orders, products] = await Promise.all([fetchOrders(), fetchProducts()]);
  const productsById = Object.fromEntries(products.map((p) => [String(p.id), p]));
  const usersById = await fetchPublicUsersByIds([
    ...orders.map((o) => o.buyer_id),
    ...products.map((p) => p.vendor_id),
  ]);
  container.innerHTML = orders.map((order) => buyerOrderCard(order, productsById, usersById)).join('') || '<div class="alert alert-info">Aucune commande.</div>';
}

async function patchOrder(orderId, data) {
  const response = await fetch(`${CONFIG.API_ORDERS_URL}/api/orders/${orderId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    alert(err.error || 'Impossible de mettre a jour la commande.');
    return false;
  }

  await loadVendorOrders();
  return true;
}

async function updateOrderLogistics(orderId) {
  const card = document.getElementById(`delivery-${orderId}`).closest('.order-card');
  await patchOrder(orderId, {
    status: card?.dataset.orderStatus || 'pending',
    estimated_delivery: document.getElementById(`delivery-${orderId}`).value,
    vendor_note: document.getElementById(`note-${orderId}`).value,
  });
}

async function setOrderStatus(orderId, status) {
  await patchOrder(orderId, {
    status,
    estimated_delivery: document.getElementById(`delivery-${orderId}`)?.value || null,
    vendor_note: document.getElementById(`note-${orderId}`)?.value || '',
  });
}

window.updateOrderLogistics = updateOrderLogistics;
window.setOrderStatus = setOrderStatus;

document.getElementById('create-order-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const productIdFromQuery = new URLSearchParams(window.location.search).get('product_id');
  const data = {
    ...(productIdFromQuery ? { product_id: Number(productIdFromQuery) } : {}),
    quantity: document.getElementById('qty').value,
    city: document.getElementById('city').value,
    delivery_address: document.getElementById('address').value,
    phone: document.getElementById('phone').value,
    payment_method: document.getElementById('payment_method')?.value || 'cash',
  };

  const response = await fetch(`${CONFIG.API_ORDERS_URL}/api/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(data),
  });

  if (response.ok) {
    alert('Commande reussie !');
    window.location.href = 'my_orders.html';
    return;
  }

  const err = await response.json().catch(() => ({}));
  alert(err?.error || err?.detail || 'Erreur lors de la commande.');
});

document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('orders-list-container');
  if (!container) return;

  try {
    if (document.body.dataset.ordersView === 'vendor') await loadVendorOrders();
    else if (document.body.dataset.ordersView === 'admin') await loadAdminOrders();
    else await loadBuyerOrders();
  } catch (error) {
    container.innerHTML = '<div class="alert alert-danger">Erreur de connexion aux services.</div>';
  }
});
