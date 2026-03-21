function filtrarProductos(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-productos tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}

function confirmarEliminarProducto(productoId, nombre) {
  const form = document.getElementById("form-eliminar");
  const label = document.getElementById("modal-username");
  if (!form || !label) {
    return;
  }

  form.action = `/productos/${productoId}/eliminar`;
  label.textContent = nombre;
  const modal = new bootstrap.Modal(document.getElementById("modalEliminar"));
  modal.show();
}
