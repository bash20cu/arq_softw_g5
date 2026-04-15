function confirmarEliminar(id, username) {
  const modalUsername = document.getElementById("modal-username");
  const formEliminar = document.getElementById("form-eliminar");
  const modalElement = document.getElementById("modalEliminar");

  if (!modalUsername || !formEliminar || !modalElement) {
    return;
  }

  modalUsername.textContent = username;
  formEliminar.action = `/usuarios/${id}/eliminar`;
  new bootstrap.Modal(modalElement).show();
}

setTimeout(() => {
  document.querySelectorAll(".alert").forEach((alertElement) => {
    bootstrap.Alert.getOrCreateInstance(alertElement).close();
  });
}, 4000);
