/* ============================================================
   ProPat — base.js
   Utilidades globales compartidas en todas las páginas
   ============================================================ */

/**
 * Muestra una alerta en el elemento indicado.
 * @param {string} selector  - Selector CSS del elemento .pp-alert
 * @param {'success'|'danger'|'warning'} type
 * @param {string} message
 * @param {number} [autoDismiss=0] - ms para ocultar automáticamente (0 = nunca)
 */
window.ppAlert = function (selector, type, message, autoDismiss = 0) {
  const el = document.querySelector(selector);
  if (!el) return;
  el.className = `pp-alert pp-alert-${type} show`;
  el.textContent = message;
  if (autoDismiss > 0) {
    setTimeout(() => el.classList.remove('show'), autoDismiss);
  }
};

/**
 * Cierra/oculta una alerta.
 * @param {string} selector
 */
window.ppAlertClear = function (selector) {
  const el = document.querySelector(selector);
  if (el) el.classList.remove('show');
};

/**
 * Abre un modal (agrega clase .open al overlay).
 * @param {string} modalId - ID del elemento .pp-modal-overlay
 */
window.ppModalOpen = function (modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.add('open');
};

/**
 * Cierra un modal.
 * @param {string} modalId
 */
window.ppModalClose = function (modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove('open');
};

/**
 * Cierra el modal si el clic fue en el overlay (fondo oscuro).
 * Llama a esta función en el onclick del overlay.
 * @param {Event} event
 * @param {string} modalId
 */
window.ppModalBackdrop = function (event, modalId) {
  if (event.target === event.currentTarget) ppModalClose(modalId);
};

/**
 * Formatea un número como precio en colones.
 * @param {number|string} value
 * @returns {string}  Ej: "₡1,250.00"
 */
window.ppPrice = function (value) {
  return '₡' + Number(value).toLocaleString('es-CR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

/**
 * Convierte una cadena ISO de fecha a formato legible.
 * @param {string|null} isoString
 * @returns {string}  Ej: "12/04/2025"
 */
window.ppDate = function (isoString) {
  if (!isoString) return '—';
  return isoString.split('T')[0].split('-').reverse().join('/');
};

/**
 * Genera el HTML de un badge de estado de orden.
 * @param {string} estado
 * @returns {string}
 */
window.ppOrderBadge = function (estado) {
  const map = {
    'En preparacion':                  ['pp-badge-yellow', '⏳'],
    'Listo para envio o recoleccion':  ['pp-badge-blue',   '📫'],
    'Entregado al cliente':            ['pp-badge-green',  '✅'],
    'Cancelado':                       ['pp-badge-red',    '❌'],
  };
  const [cls, icon] = map[estado] || ['pp-badge-gray', '•'];
  return `<span class="pp-badge ${cls}">${icon} ${estado}</span>`;
};

/**
 * Genera el HTML de un badge de estado de cliente.
 * @param {string} estado
 * @returns {string}
 */
window.ppClientBadge = function (estado) {
  const map = {
    Activo:   'pp-badge-green',
    Inactivo: 'pp-badge-gray',
    VIP:      'pp-badge-yellow',
    Moroso:   'pp-badge-red',
  };
  return `<span class="pp-badge ${map[estado] || 'pp-badge-gray'}">${estado}</span>`;
};

/**
 * Wrapper simple para consumir la API REST de ProPat.
 * - Incluye cookies de sesión (auth por session cookie)
 * - Maneja errores comunes y devuelve JSON
 *
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
window.ppFetch = async function (url, options = {}) {
  const headers = {
    Accept: 'application/json',
    ...(options.headers || {}),
  };

  const res = await fetch(url, {
    credentials: 'same-origin',
    ...options,
    headers,
  });

  let data = null;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    data = await res.json();
  } else {
    const text = await res.text();
    data = text ? { message: text } : null;
  }

  if (!res.ok) {
    const msg =
      (data && (data.error || data.message)) ||
      `Error HTTP ${res.status}`;
    throw new Error(msg);
  }

  return data;
};

/**
 * Carga el select de provincias desde la API.
 * @param {string} selectId - ID del <select>
 */
window.ppLoadProvincias = async function (selectId) {
  const res  = await fetch('/api/v1/catalogos/provincias');
  const data = await res.json();
  const sel  = document.getElementById(selectId);
  if (!sel) return;
  data.forEach(p => {
    const opt = document.createElement('option');
    opt.value       = p.id_provincia;
    opt.textContent = p.nombre;
    sel.appendChild(opt);
  });
};

/**
 * Carga cantones según provincia y los pone en un select.
 * @param {number|string} provinciaId
 * @param {string} cantonSelectId
 * @param {string} distritoSelectId - se resetea y deshabilita
 */
window.ppLoadCantones = async function (provinciaId, cantonSelectId, distritoSelectId) {
  const cantonSel  = document.getElementById(cantonSelectId);
  const distSel    = document.getElementById(distritoSelectId);
  cantonSel.innerHTML  = '<option value="">— Cantón —</option>';
  distSel.innerHTML    = '<option value="">— Distrito —</option>';
  cantonSel.disabled   = !provinciaId;
  distSel.disabled     = true;
  if (!provinciaId) return;
  const data = await (await fetch(`/api/v1/catalogos/cantones?provincia_id=${provinciaId}`)).json();
  data.forEach(c => {
    const opt = document.createElement('option');
    opt.value       = c.id_canton;
    opt.textContent = c.nombre;
    cantonSel.appendChild(opt);
  });
};

/**
 * Carga distritos según cantón y los pone en un select.
 * @param {number|string} cantonId
 * @param {string} distritoSelectId
 */
window.ppLoadDistritos = async function (cantonId, distritoSelectId) {
  const distSel = document.getElementById(distritoSelectId);
  distSel.innerHTML = '<option value="">— Distrito —</option>';
  distSel.disabled  = !cantonId;
  if (!cantonId) return;
  const data = await (await fetch(`/api/v1/catalogos/distritos?canton_id=${cantonId}`)).json();
  data.forEach(d => {
    const opt = document.createElement('option');
    opt.value       = d.id_distrito;
    opt.textContent = d.nombre;
    distSel.appendChild(opt);
  });
  distSel.disabled = false;
};

/**
 * Enlaza tres selects (provincia → cantón → distrito) usando la API.
 * @param {string} provinciaSelectId
 * @param {string} cantonSelectId
 * @param {string} distritoSelectId
 */
window.ppBindLocation = function (provinciaSelectId, cantonSelectId, distritoSelectId) {
  const provSel = document.getElementById(provinciaSelectId);
  const cantSel = document.getElementById(cantonSelectId);
  const distSel = document.getElementById(distritoSelectId);
  if (!provSel || !cantSel || !distSel) return;

  provSel.addEventListener('change', async () => {
    await ppLoadCantones(provSel.value, cantonSelectId, distritoSelectId);
  });

  cantSel.addEventListener('change', async () => {
    await ppLoadDistritos(cantSel.value, distritoSelectId);
  });
};

/* ── Marcar link activo en el navbar ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pp-nav-links .nav-link').forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
      link.classList.add('active');
    }
  });
});