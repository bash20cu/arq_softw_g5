/* ProPat — productos.js */

let editingProductId = null;

/* ── Tabla ───────────────────────────────────────────────────── */
async function loadProducts() {
  const data = await ppFetch('/api/v1/productos');
  const body = document.getElementById('productsTable');
  body.innerHTML = '';

  if (!data || !data.length) {
    body.innerHTML = '<tr><td colspan="9" class="table-empty">Sin productos registrados</td></tr>';
    return;
  }

  data.forEach(p => {
    const activeBadge = p.activo
      ? '<span class="pp-badge pp-badge-green">Activo</span>'
      : '<span class="pp-badge pp-badge-gray">Inactivo</span>';

    const stockBadge = p.stock <= 5
      ? `<span class="pp-badge pp-badge-red">${p.stock}</span>`
      : `<span class="pp-badge pp-badge-green">${p.stock}</span>`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="text-mono text-muted">${p.id_producto}</td>
      <td>
        <strong>${p.nombre}</strong>
        <br><small class="text-muted">${p.color_estilo || '—'}</small>
      </td>
      <td class="text-mono text-small">${p.codigo_barras || '—'}</td>
      <td>${ppPrice(p.precio_base)}</td>
      <td>${p.iva_porcentaje}%</td>
      <td class="text-strong">${ppPrice(p.precio_actual)}</td>
      <td>${stockBadge}</td>
      <td>${activeBadge}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-pp btn-pp-ghost btn-pp-sm" data-action="edit" data-product='${JSON.stringify(p)}'>Editar</button>
          <button class="btn-pp btn-pp-danger btn-pp-sm" data-action="delete" data-id="${p.id_producto}" data-nombre="${p.nombre}">Eliminar</button>
        </div>
      </td>
    `;
    body.appendChild(tr);
  });
}

/* ── Modal ───────────────────────────────────────────────────── */
function openNewProductModal() {
  editingProductId = null;
  document.getElementById('modalProductoTitle').textContent = 'Nuevo producto';
  document.getElementById('productoSubmitBtn').textContent  = 'Guardar producto';
  document.getElementById('productForm').reset();
  document.getElementById('fldProductoId').value = '';
  document.getElementById('chkActivo').checked   = true;
  ppAlertClear('#productoAlert');
  ppModalOpen('modalProducto');
}

function openEditProductModal(p) {
  editingProductId = p.id_producto;
  document.getElementById('modalProductoTitle').textContent = 'Editar producto';
  document.getElementById('productoSubmitBtn').textContent  = 'Actualizar producto';

  const f = document.getElementById('productForm');
  f.querySelector('[name="nombre"]').value         = p.nombre;
  f.querySelector('[name="descripcion"]').value     = p.descripcion   || '';
  f.querySelector('[name="fotografia_url"]').value  = p.fotografia_url || '';
  f.querySelector('[name="color_estilo"]').value    = p.color_estilo  || '';
  f.querySelector('[name="codigo_barras"]').value   = p.codigo_barras || '';
  f.querySelector('[name="precio_base"]').value     = p.precio_base;
  f.querySelector('[name="iva_porcentaje"]').value  = p.iva_porcentaje;
  f.querySelector('[name="stock"]').value           = p.stock;
  document.getElementById('chkActivo').checked      = p.activo;

  ppAlertClear('#productoAlert');
  ppModalOpen('modalProducto');
}

/* ── Submit ──────────────────────────────────────────────────── */
document.getElementById('productForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;

  const payload = {
    nombre:         f.querySelector('[name="nombre"]').value.trim(),
    descripcion:    f.querySelector('[name="descripcion"]').value.trim() || null,
    fotografia_url: f.querySelector('[name="fotografia_url"]').value.trim() || null,
    color_estilo:   f.querySelector('[name="color_estilo"]').value.trim()  || null,
    codigo_barras:  f.querySelector('[name="codigo_barras"]').value.trim() || null,
    precio_base:    Number(f.querySelector('[name="precio_base"]').value),
    iva_porcentaje: Number(f.querySelector('[name="iva_porcentaje"]').value),
    stock:          Number(f.querySelector('[name="stock"]').value),
    activo:         document.getElementById('chkActivo').checked,
  };

  const isEdit = editingProductId !== null;
  const url    = isEdit ? `/api/v1/productos/${editingProductId}` : '/api/v1/productos';
  const method = isEdit ? 'PUT' : 'POST';

  const res  = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#productoAlert', 'danger', data.error || 'No fue posible guardar');
    return;
  }

  ppModalClose('modalProducto');
  ppAlert('#productoPageAlert', 'success', isEdit ? 'Producto actualizado' : 'Producto creado', 3000);
  loadProducts();
});

/* ── Eliminar ────────────────────────────────────────────────── */
async function deleteProduct(id, nombre) {
  if (!confirm(`¿Eliminar "${nombre}"? Esta acción no se puede deshacer.`)) return;

  const res  = await fetch(`/api/v1/productos/${id}`, { method: 'DELETE' });
  const data = await res.json();

  if (!res.ok) {
    alert(data.error || 'No fue posible eliminar el producto');
    return;
  }

  ppAlert('#productoPageAlert', 'success', 'Producto eliminado', 3000);
  loadProducts();
}

/* ── Event delegation (tabla) ────────────────────────────────── */
document.getElementById('productsTable').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-action]');
  if (!btn) return;

  if (btn.dataset.action === 'edit') {
    openEditProductModal(JSON.parse(btn.dataset.product));
  }
  if (btn.dataset.action === 'delete') {
    deleteProduct(btn.dataset.id, btn.dataset.nombre);
  }
});

document.getElementById('btnNuevoProducto').addEventListener('click', openNewProductModal);
document.getElementById('reloadProducts').addEventListener('click', loadProducts);

loadProducts();