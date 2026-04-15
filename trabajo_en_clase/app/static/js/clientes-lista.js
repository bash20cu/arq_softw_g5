function filtrarClientes(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-clientes tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}

function confirmarEliminarCliente(clienteId, nombre) {
  const form = document.getElementById("form-eliminar");
  const label = document.getElementById("modal-username");
  if (!form || !label) {
    return;
  }

  form.action = `/clientes/${clienteId}/eliminar`;
  label.textContent = nombre;
  const modal = new bootstrap.Modal(document.getElementById("modalEliminar"));
  modal.show();
}
