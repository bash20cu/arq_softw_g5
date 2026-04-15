/* ProPat — clientes.js */

let editingClientId = null;

/* ── Tabla ───────────────────────────────────────────────────── */
async function loadClients() {
  const data = await ppFetch('/api/v1/clientes');
  const body = document.getElementById('clientsTable');
  body.innerHTML = '';

  if (!data || !data.length) {
    body.innerHTML = '<tr><td colspan="8" class="table-empty">Sin clientes registrados</td></tr>';
    return;
  }

  data.forEach(c => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="text-mono text-muted">${c.id_cliente}</td>
      <td>
        <strong>${c.nombre_completo}</strong>
        ${c.cedula_persona
          ? `<br><small class="text-muted">Cédula: ${c.cedula_persona}</small>`
          : ''}
      </td>
      <td><span class="pp-badge pp-badge-gray">${c.tipo_cliente}</span></td>
      <td class="text-small">${c.email}</td>
      <td class="text-small">${c.telefono || '—'}</td>
      <td class="text-mono">${c.puntos_lealtad}</td>
      <td>${ppClientBadge(c.estado_cliente)}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-pp btn-pp-ghost btn-pp-sm"
                  data-action="edit"
                  data-client='${JSON.stringify(c)}'>Editar</button>
          <button class="btn-pp btn-pp-danger btn-pp-sm"
                  data-action="delete"
                  data-id="${c.id_cliente}"
                  data-nombre="${c.nombre_completo}">Eliminar</button>
        </div>
      </td>
    `;
    body.appendChild(tr);
  });
}

/* ── Modal: abrir nuevo ──────────────────────────────────────── */
function openNewClientModal() {
  editingClientId = null;
  document.getElementById('modalClienteTitle').textContent  = 'Nuevo cliente';
  document.getElementById('clienteSubmitBtn').textContent   = 'Guardar cliente';
  document.getElementById('clientForm').reset();
  document.getElementById('fldClienteId').value = '';
  document.getElementById('cApellidoBox').style.display = '';

  // Resetear ubicación
  document.getElementById('cCanton').innerHTML  = '<option value="">— Cantón —</option>';
  document.getElementById('cDistrito').innerHTML = '<option value="">— Distrito —</option>';
  document.getElementById('cCanton').disabled   = true;
  document.getElementById('cDistrito').disabled = true;

  ppAlertClear('#clienteAlert');
  ppModalOpen('modalCliente');
}

/* ── Modal: abrir edición ────────────────────────────────────── */
function openEditClientModal(c) {
  editingClientId = c.id_cliente;
  document.getElementById('modalClienteTitle').textContent = 'Editar cliente';
  document.getElementById('clienteSubmitBtn').textContent  = 'Actualizar cliente';

  const f = document.getElementById('clientForm');
  f.querySelector('[name="tipo_cliente"]').value   = c.tipo_cliente;
  f.querySelector('[name="estado_cliente"]').value = c.estado_cliente;
  f.querySelector('[name="nombre"]').value         = c.nombre;
  f.querySelector('[name="apellido"]').value        = c.apellido   || '';
  f.querySelector('[name="email"]').value           = c.email;
  f.querySelector('[name="telefono"]').value        = c.telefono   || '';
  f.querySelector('[name="cedula_persona"]').value  = c.cedula_persona || '';
  f.querySelector('[name="direccion"]').value       = c.direccion  || '';
  f.querySelector('[name="puntos_lealtad"]').value  = c.puntos_lealtad;

  document.getElementById('cApellidoBox').style.display =
    c.tipo_cliente === 'Empresa' ? 'none' : '';

  ppAlertClear('#clienteAlert');
  ppModalOpen('modalCliente');
}

/* ── Ocultar apellido para empresas ──────────────────────────── */
document.getElementById('cTipo').addEventListener('change', function () {
  document.getElementById('cApellidoBox').style.display =
    this.value === 'Empresa' ? 'none' : '';
});

/* ── Submit (crear / editar) ─────────────────────────────────── */
document.getElementById('clientForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;

  const payload = {
    tipo_cliente:   f.querySelector('[name="tipo_cliente"]').value,
    estado_cliente: f.querySelector('[name="estado_cliente"]').value,
    nombre:         f.querySelector('[name="nombre"]').value.trim(),
    apellido:       f.querySelector('[name="apellido"]').value.trim() || null,
    email:          f.querySelector('[name="email"]').value.trim(),
    telefono:       f.querySelector('[name="telefono"]').value.trim()       || null,
    cedula_persona: f.querySelector('[name="cedula_persona"]').value.trim() || null,
    direccion:      f.querySelector('[name="direccion"]').value.trim()      || null,
    puntos_lealtad: Number(f.querySelector('[name="puntos_lealtad"]').value),
    id_distrito:    Number(document.getElementById('cDistrito').value) || null,
  };

  const isEdit = editingClientId !== null;
  const url    = isEdit ? `/api/v1/clientes/${editingClientId}` : '/api/v1/clientes';
  const method = isEdit ? 'PUT' : 'POST';

  const res  = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#clienteAlert', 'danger', data.error || 'No fue posible guardar');
    return;
  }

  ppModalClose('modalCliente');
  ppAlert('#clientePageAlert', 'success',
    isEdit ? 'Cliente actualizado' : 'Cliente creado', 3000);
  loadClients();
});

/* ── Eliminar ────────────────────────────────────────────────── */
async function deleteClient(id, nombre) {
  if (!confirm(`¿Eliminar al cliente "${nombre}"?`)) return;

  const res  = await fetch(`/api/v1/clientes/${id}`, { method: 'DELETE' });
  const data = await res.json();

  if (!res.ok) {
    alert(data.error || 'No fue posible eliminar');
    return;
  }

  ppAlert('#clientePageAlert', 'success', 'Cliente eliminado', 3000);
  loadClients();
}

/* ── Event delegation (tabla) ────────────────────────────────── */
document.getElementById('clientsTable').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-action]');
  if (!btn) return;

  if (btn.dataset.action === 'edit')
    openEditClientModal(JSON.parse(btn.dataset.client));

  if (btn.dataset.action === 'delete')
    deleteClient(btn.dataset.id, btn.dataset.nombre);
});

/* ── Botones estáticos ───────────────────────────────────────── */
document.getElementById('btnNuevoCliente').addEventListener('click', openNewClientModal);
document.getElementById('reloadClients').addEventListener('click', loadClients);

/* ── Init ────────────────────────────────────────────────────── */
ppLoadProvincias('cProvincia');
ppBindLocation('cProvincia', 'cCanton', 'cDistrito');
loadClients();