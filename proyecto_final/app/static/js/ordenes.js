/* ProPat — ordenes.js */

/* ── Toggle formulario nueva orden ──────────────────────────── */
document.getElementById('btnToggleForm').addEventListener('click', () => {
  document.getElementById('orderFormBox').classList.add('open');
});

document.getElementById('btnCancelForm').addEventListener('click', () => {
  document.getElementById('orderFormBox').classList.remove('open');
});

/* ── Cargar selects del formulario ───────────────────────────── */
async function loadOrderFormSelects() {
  const [clients, products] = await Promise.all([
    ppFetch('/api/v1/clientes'),
    ppFetch('/api/v1/productos'),
  ]);

  const cSel = document.getElementById('orderClientSelect');
  cSel.innerHTML = '';
  (clients || []).forEach(c =>
    cSel.insertAdjacentHTML('beforeend',
      `<option value="${c.id_cliente}">${c.nombre_completo}</option>`));

  const pSel = document.getElementById('orderProductSelect');
  pSel.innerHTML = '';
  (products || []).forEach(p =>
    pSel.insertAdjacentHTML('beforeend',
      `<option value="${p.id_producto}">${p.nombre} (stock: ${p.stock})</option>`));
}

/* ── Tabla de órdenes ────────────────────────────────────────── */
async function loadOrders() {
  const data = await ppFetch('/api/v1/ordenes');
  const body = document.getElementById('ordersTable');
  body.innerHTML = '';

  if (!data || !data.length) {
    body.innerHTML = '<tr><td colspan="7" class="table-empty">Sin órdenes registradas</td></tr>';
    return;
  }

  data.forEach(o => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="text-mono text-muted">${o.id_orden}</td>
      <td>${o.nombre_cliente || o.id_cliente}</td>
      <td class="text-muted text-small">${o.username_usuario || '—'}</td>
      <td class="text-small text-muted">${ppDate(o.fecha_orden)}</td>
      <td>${ppOrderBadge(o.estado)}</td>
      <td class="text-strong">${ppPrice(o.total)}</td>
      <td>
        <button class="btn-pp btn-pp-ghost btn-pp-sm"
                data-action="pay"
                data-id="${o.id_orden}">Pagos</button>
      </td>
    `;
    body.appendChild(tr);
  });
}

/* ── Crear orden ─────────────────────────────────────────────── */
document.getElementById('orderForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;

  const payload = {
    id_cliente: Number(document.getElementById('orderClientSelect').value),
    detalles: [{
      id_producto: Number(document.getElementById('orderProductSelect').value),
      cantidad:    Number(f.querySelector('[name="cantidad"]').value),
    }],
    estado: 'En preparacion',
  };

  const res  = await fetch('/api/v1/ordenes', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#orderAlert', 'danger', data.error || 'No fue posible crear la orden');
    return;
  }

  ppAlert('#orderAlert', 'success', `Orden #${data.id_orden} creada`);
  document.getElementById('payOrderId').value = data.id_orden;
  document.getElementById('orderFormBox').classList.remove('open');
  loadOrders();
  loadOrderFormSelects();   // refresca stock en el select
});

/* ── Tabla de pagos ──────────────────────────────────────────── */
async function loadPayments(orderId) {
  const data = await ppFetch(`/api/v1/ordenes/${orderId}/pagos`);
  const body = document.getElementById('paymentsTable');
  body.innerHTML = '';

  if (!data || !data.length) {
    body.innerHTML = '<tr><td colspan="4" class="table-empty">Sin pagos para esta orden</td></tr>';
    return;
  }

  data.forEach(p => {
    const stateMap = {
      Completado: 'pp-badge-green',
      Pendiente:  'pp-badge-yellow',
    };
    const cls = stateMap[p.estado] || 'pp-badge-gray';
    const tr  = document.createElement('tr');
    tr.innerHTML = `
      <td class="text-mono">${p.id_pago}</td>
      <td class="text-small" style="max-width:120px;overflow:hidden;text-overflow:ellipsis;">
        ${p.referencia_externa || '—'}
      </td>
      <td><span class="pp-badge ${cls}">${p.estado}</span></td>
      <td>$${Number(p.monto).toFixed(2)}</td>
    `;
    body.appendChild(tr);
  });
}

/* ── Event delegation: click en fila → autocompletar ID ──────── */
document.getElementById('ordersTable').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-action="pay"]');
  if (!btn) return;
  document.getElementById('payOrderId').value = btn.dataset.id;
  loadPayments(btn.dataset.id);
  document.querySelector('.payments-grid').scrollIntoView({ behavior: 'smooth' });
});

/* ── Crear orden PayPal ──────────────────────────────────────── */
document.getElementById('btnCreatePaypal').addEventListener('click', async () => {
  const orderId = document.getElementById('payOrderId').value;
  if (!orderId) { ppAlert('#paymentAlert', 'warning', 'Indica un ID de orden'); return; }

  const res  = await fetch(`/api/v1/ordenes/${orderId}/pagos/paypal/crear-orden`,
    { method: 'POST' });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#paymentAlert', 'danger', data.error || 'Error al crear orden PayPal');
    return;
  }

  ppAlert('#paymentAlert', 'success',
    `Pago #${data.payment.id_pago} creado. Apruébalo antes de capturar.`);
  document.getElementById('payPaymentId').value = data.payment.id_pago;

  if (data.approve_url) {
    document.getElementById('approveLink').href = data.approve_url;
    document.getElementById('approveBox').classList.add('open');
  }

  loadPayments(orderId);
});

/* ── Ver pagos ───────────────────────────────────────────────── */
document.getElementById('btnLoadPayments').addEventListener('click', () => {
  const id = document.getElementById('payOrderId').value;
  if (!id) { ppAlert('#paymentAlert', 'warning', 'Indica un ID de orden'); return; }
  loadPayments(id);
});

/* ── Capturar pago ───────────────────────────────────────────── */
document.getElementById('btnCapture').addEventListener('click', async () => {
  const payId   = document.getElementById('payPaymentId').value;
  const orderId = document.getElementById('payOrderId').value;
  if (!payId) { ppAlert('#paymentAlert', 'warning', 'Indica un ID de pago'); return; }

  const res  = await fetch(`/api/v1/pagos/${payId}/capturar`, { method: 'POST' });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#paymentAlert', 'danger', data.error || 'Error al capturar');
    return;
  }

  ppAlert('#paymentAlert', 'success', `Pago #${payId} capturado correctamente`, 3000);
  if (orderId) loadPayments(orderId);
});

/* ── Reload ──────────────────────────────────────────────────── */
document.getElementById('reloadOrders').addEventListener('click', loadOrders);

/* ── Init ────────────────────────────────────────────────────── */
loadOrderFormSelects();
loadOrders();