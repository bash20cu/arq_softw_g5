/* ProPat — personas.js */

let editingCedula = null;

/* ── Tabla ───────────────────────────────────────────────────── */
async function loadPersonas() {
  const body = document.getElementById('personasTable');
  body.innerHTML = '<tr><td colspan="6" class="table-empty">Cargando...</td></tr>';

  try {
    const data = await ppFetch('/api/v1/personas');
    body.innerHTML = '';

    if (!data || !data.length) {
      body.innerHTML = '<tr><td colspan="6" class="table-empty">Sin personas registradas</td></tr>';
      return;
    }

    data.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="text-mono text-small">${p.cedula}</td>
        <td><strong>${p.nombre} ${p.apellido}</strong></td>
        <td class="text-small">${p.email}</td>
        <td class="text-small">${p.telefono || '—'}</td>
        <td class="text-small text-muted">${ppDate(p.fecha_registro)}</td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn-pp btn-pp-ghost btn-pp-sm"
                    data-action="edit"
                    data-persona='${JSON.stringify(p)}'>Editar</button>
            <button class="btn-pp btn-pp-danger btn-pp-sm"
                    data-action="delete"
                    data-cedula="${p.cedula}"
                    data-nombre="${p.nombre} ${p.apellido}">Eliminar</button>
          </div>
        </td>
      `;
      body.appendChild(tr);
    });
  } catch (error) {
    body.innerHTML = `<tr><td colspan="6" class="table-empty">No fue posible cargar personas: ${error.message}</td></tr>`;
    ppAlert('#personaPageAlert', 'danger', error.message || 'No fue posible cargar personas');
  }
}

/* ── Modal: abrir nuevo ──────────────────────────────────────── */
function openNewPersonaModal() {
  editingCedula = null;
  document.getElementById('modalPersonaTitle').textContent = 'Nueva persona';
  document.getElementById('personaSubmitBtn').textContent  = 'Guardar persona';
  document.getElementById('personaForm').reset();
  document.getElementById('pCedula').disabled = false;

  document.getElementById('pCanton').innerHTML  = '<option value="">— Cantón —</option>';
  document.getElementById('pDistrito').innerHTML = '<option value="">— Distrito —</option>';
  document.getElementById('pCanton').disabled   = true;
  document.getElementById('pDistrito').disabled = true;

  ppAlertClear('#personaAlert');
  ppModalOpen('modalPersona');
}

/* ── Modal: abrir edición ────────────────────────────────────── */
function openEditPersonaModal(p) {
  editingCedula = p.cedula;
  document.getElementById('modalPersonaTitle').textContent = 'Editar persona';
  document.getElementById('personaSubmitBtn').textContent  = 'Actualizar persona';

  const f = document.getElementById('personaForm');
  document.getElementById('pCedula').value    = p.cedula;
  document.getElementById('pCedula').disabled = true;   // la cédula es PK, no se cambia
  f.querySelector('[name="nombre"]').value    = p.nombre;
  f.querySelector('[name="apellido"]').value  = p.apellido;
  f.querySelector('[name="email"]').value     = p.email;
  f.querySelector('[name="telefono"]').value  = p.telefono || '';

  ppAlertClear('#personaAlert');
  ppModalOpen('modalPersona');
}

/* ── Submit (crear / editar) ─────────────────────────────────── */
document.getElementById('personaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;

  const isEdit = editingCedula !== null;

  const payload = {
    nombre:      f.querySelector('[name="nombre"]').value.trim(),
    apellido:    f.querySelector('[name="apellido"]').value.trim(),
    email:       f.querySelector('[name="email"]').value.trim(),
    telefono:    f.querySelector('[name="telefono"]').value.trim() || null,
    id_distrito: Number(document.getElementById('pDistrito').value) || null,
  };

  // Solo en creación se envía la cédula
  if (!isEdit) {
    payload.cedula = document.getElementById('pCedula').value.trim();
  }

  const url    = isEdit ? `/api/v1/personas/${editingCedula}` : '/api/v1/personas';
  const method = isEdit ? 'PUT' : 'POST';

  const res  = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    ppAlert('#personaAlert', 'danger', data.error || 'No fue posible guardar');
    return;
  }

  ppModalClose('modalPersona');
  ppAlert('#personaPageAlert', 'success',
    isEdit ? 'Persona actualizada' : 'Persona creada', 3000);
  loadPersonas();
});

/* ── Eliminar ────────────────────────────────────────────────── */
async function deletePersona(cedula, nombre) {
  if (!confirm(`¿Eliminar a "${nombre}" (cédula: ${cedula})?`)) return;

  const res  = await fetch(`/api/v1/personas/${cedula}`, { method: 'DELETE' });
  const data = await res.json();

  if (!res.ok) {
    alert(data.error || 'No fue posible eliminar');
    return;
  }

  ppAlert('#personaPageAlert', 'success', 'Persona eliminada', 3000);
  loadPersonas();
}

/* ── Event delegation (tabla) ────────────────────────────────── */
document.getElementById('personasTable').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-action]');
  if (!btn) return;

  if (btn.dataset.action === 'edit')
    openEditPersonaModal(JSON.parse(btn.dataset.persona));

  if (btn.dataset.action === 'delete')
    deletePersona(btn.dataset.cedula, btn.dataset.nombre);
});

/* ── Botones estáticos ───────────────────────────────────────── */
document.getElementById('btnNuevoPersona').addEventListener('click', openNewPersonaModal);
document.getElementById('reloadPersonas').addEventListener('click', loadPersonas);

/* ── Init ────────────────────────────────────────────────────── */
ppLoadProvincias('pProvincia');
ppBindLocation('pProvincia', 'pCanton', 'pDistrito');
loadPersonas();
