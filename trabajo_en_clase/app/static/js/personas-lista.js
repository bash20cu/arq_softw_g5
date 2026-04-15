function filtrarPersonas(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-personas tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}

function confirmarEliminarPersona(cedula, nombre) {
  const form = document.getElementById("form-eliminar");
  const label = document.getElementById("modal-username");
  if (!form || !label) {
    return;
  }

  form.action = `/personas/${cedula}/eliminar`;
  label.textContent = nombre;
  const modal = new bootstrap.Modal(document.getElementById("modalEliminar"));
  modal.show();
}
