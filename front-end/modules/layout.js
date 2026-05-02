window.MedLayout = (function () {
  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function clearSession() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    const icon = document.getElementById('themeIcon');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill fs-5 text-warning' : 'bi bi-moon-stars-fill fs-5 text-dark';
    }
  }

  function roleLinks(role) {
    if (role === 'vendeur') {
      return [
        ['../users/dashboard.html', 'bi-speedometer2', 'Dashboard'],
        ['../products/my-products.html', 'bi-box-seam', 'Mes produits'],
        ['../products/add_product.html', 'bi-plus-circle', 'Ajouter produit'],
        ['../orders/vendor_orders.html', 'bi-receipt-cutoff', 'Commandes reçues'],
        ['../products/Marketplace.html', 'bi-shop', 'Marketplace'],
      ];
    }

    if (role === 'admin') {
      return [
        ['../users/dashboard.html', 'bi-speedometer2', 'Dashboard'],
        ['../orders/admin_history.html', 'bi-clock-history', 'Historique commandes'],
        ['../products/Marketplace.html', 'bi-shop', 'Marketplace'],
        ['http://localhost:8000/admin/', 'bi-person-gear', 'Django admin'],
      ];
    }

    return [
      ['../users/dashboard.html', 'bi-speedometer2', 'Dashboard'],
      ['../products/Marketplace.html', 'bi-shop', 'Accueil produits'],
      ['../orders/my_orders.html', 'bi-bag-check', 'Mes commandes'],
    ];
  }

  function init() {
    const isAuth = Boolean(window.getAccessToken && window.getAccessToken());
    const role = localStorage.getItem('user_role') || '';
    const username = localStorage.getItem('username') || 'User';
    const initial = username.slice(0, 1).toUpperCase();
    const roleLabel = role === 'vendeur' ? 'Vendeur' : role === 'admin' ? 'Admin' : 'Acheteur';

    const nav = document.createElement('nav');
    nav.className = 'navbar navbar-expand-lg navbar-premium sticky-top';
    nav.innerHTML = `
      <div class="container">
        <a class="navbar-brand-premium" href="../../index.html">
          <div class="logo-container"><i class="bi bi-heart-pulse-fill"></i></div>
          <div class="brand-text">
            <span class="brand-name">MedCONNECT</span>
            <span class="brand-tagline">Solutions B2B</span>
          </div>
        </a>
        <div class="d-flex align-items-center gap-2">
          <a class="btn btn-outline-secondary btn-sm rounded-pill" href="../products/Marketplace.html">Accueil</a>
          <button id="themeToggle" class="btn btn-link nav-link border-0 p-0 shadow-none">
            <i class="bi bi-moon-stars-fill fs-5" id="themeIcon"></i>
          </button>
          ${
            isAuth
              ? `<div class="nav-profile-pill" id="profileBtn"><div class="nav-avatar">${escapeHtml(initial)}</div><div class="d-none d-md-block"><div class="fw-bold lh-1" style="font-size:.85rem;">${escapeHtml(username)}</div><div class="text-muted small" style="font-size:.7rem;">${roleLabel}</div></div></div>`
              : `<a href="../users/login.html" class="btn btn-primary rounded-pill px-4 fw-bold shadow-sm">Connexion</a>`
          }
        </div>
      </div>
    `;
    document.body.prepend(nav);

    if (isAuth) {
      const sidebar = document.createElement('div');
      sidebar.className = 'sidebar';
      sidebar.id = 'sidebar';
      sidebar.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Espace membre</h5>
          <button id="closeSidebar" class="btn-close shadow-none"></button>
        </div>
        <div class="text-center mb-4">
          <div class="profile-avatar-lg mx-auto mb-3">${escapeHtml(initial)}</div>
          <h6 class="fw-bold mb-1">${escapeHtml(username)}</h6>
          <p class="text-muted small mb-0">Compte ${roleLabel}</p>
        </div>
        <div class="list-group list-group-flush">
          ${roleLinks(role).map(([href, icon, label]) => `<a href="${href}" class="list-group-item"><i class="bi ${icon} me-2"></i>${label}</a>`).join('')}
          <button id="logoutBtn" class="list-group-item text-danger text-start border-0 bg-transparent mt-2"><i class="bi bi-box-arrow-right me-2"></i>Déconnexion</button>
        </div>
      `;
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      overlay.id = 'sidebarOverlay';
      document.body.appendChild(sidebar);
      document.body.appendChild(overlay);

      const toggleSidebar = (show) => {
        sidebar.classList.toggle('show', show);
        overlay.classList.toggle('show', show);
        document.body.style.overflow = show ? 'hidden' : '';
      };
      document.getElementById('profileBtn')?.addEventListener('click', () => toggleSidebar(true));
      document.getElementById('closeSidebar')?.addEventListener('click', () => toggleSidebar(false));
      overlay?.addEventListener('click', () => toggleSidebar(false));
      document.getElementById('logoutBtn')?.addEventListener('click', () => {
        clearSession();
        location.href = '../users/login.html';
      });
    }

    const footer = document.createElement('footer');
    footer.className = 'layout-footer text-center';
    footer.innerHTML = `
      <div class="container">
        <p class="mb-0">&copy; 2026 MedCONNECT-B2B. Tous droits réservés.</p>
        <p class="small mb-0">Plateforme sécurisée pour les professionnels de santé.</p>
      </div>
    `;
    document.body.appendChild(footer);

    document.getElementById('themeToggle')?.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
      setTheme(current === 'light' ? 'dark' : 'light');
    });
    setTheme(localStorage.getItem('theme') || 'light');
  }

  return { init };
})();
