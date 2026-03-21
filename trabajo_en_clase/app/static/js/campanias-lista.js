function filtrarCampanias(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-campanias tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}

function confirmarEliminarCampania(campaniaId, nombre) {
  const form = document.getElementById("form-eliminar");
  const label = document.getElementById("modal-username");
  if (!form || !label) {
    return;
  }

  form.action = `/campanias/${campaniaId}/eliminar`;
  label.textContent = nombre;
  const modal = new bootstrap.Modal(document.getElementById("modalEliminar"));
  modal.show();
}
