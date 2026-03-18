async function fillSelect(select, url, placeholder, selectedValue = "") {
  if (!select) {
    return;
  }

  select.innerHTML = `<option value="">${placeholder}</option>`;
  if (!url) {
    return;
  }

  const response = await fetch(url);
  const data = await response.json();
  data.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id_provincia || item.id_canton || item.id_distrito;
    option.textContent = item.nombre;
    if (String(option.value) === String(selectedValue)) {
      option.selected = true;
    }
    select.appendChild(option);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const provinciaSelect = document.getElementById("provinciaSelect");
  const cantonSelect = document.getElementById("cantonSelect");
  const distritoSelect = document.getElementById("distritoSelect");
  const tipoInputs = document.querySelectorAll('input[name="tipo_cliente"]');
  const apellidoGroup = document.getElementById("apellidoGroup");
  const inputApellido = document.getElementById("inputApellido");
  const labelNombre = document.getElementById("labelNombre");
  const labelApellido = document.getElementById("labelApellido");
  const cedulaPersona = document.querySelector('input[name="cedula_persona"]');

  function syncClientTypeUI() {
    const tipo = document.querySelector('input[name="tipo_cliente"]:checked')?.value || "Persona";
    const isEmpresa = tipo === "Empresa";

    if (labelNombre) {
      labelNombre.innerHTML = `${isEmpresa ? "Razón social" : "Nombre"} <span class="text-danger">*</span>`;
    }
    if (labelApellido) {
      labelApellido.innerHTML = `${isEmpresa ? "Nombre comercial / contacto" : "Apellido"}${isEmpresa ? "" : ' <span class="text-danger">*</span>'}`;
    }
    if (apellidoGroup) {
      apellidoGroup.classList.toggle("opacity-75", isEmpresa);
    }
    if (inputApellido) {
      inputApellido.required = !isEmpresa;
      inputApellido.placeholder = isEmpresa ? "Opcional" : "";
    }
    if (cedulaPersona) {
      cedulaPersona.disabled = isEmpresa;
      if (isEmpresa) {
        cedulaPersona.value = "";
      }
    }
  }

  if (!provinciaSelect || !cantonSelect || !distritoSelect) {
    syncClientTypeUI();
    tipoInputs.forEach((input) => input.addEventListener("change", syncClientTypeUI));
    return;
  }

  const selectedProvincia = provinciaSelect.dataset.selected || provinciaSelect.value;
  const selectedCanton = cantonSelect.dataset.selected || "";
  const selectedDistrito = distritoSelect.dataset.selected || "";

  if (selectedProvincia) {
    await fillSelect(
      cantonSelect,
      `/api/v1/catalogos/cantones?provincia_id=${selectedProvincia}`,
      "Seleccionar cantón...",
      selectedCanton
    );
  }

  if (selectedCanton) {
    await fillSelect(
      distritoSelect,
      `/api/v1/catalogos/distritos?canton_id=${selectedCanton}`,
      "Sin distrito",
      selectedDistrito
    );
  }

  provinciaSelect.addEventListener("change", async () => {
    await fillSelect(
      cantonSelect,
      provinciaSelect.value
        ? `/api/v1/catalogos/cantones?provincia_id=${provinciaSelect.value}`
        : "",
      "Seleccionar cantón..."
    );
    await fillSelect(distritoSelect, "", "Sin distrito");
  });

  cantonSelect.addEventListener("change", async () => {
    await fillSelect(
      distritoSelect,
      cantonSelect.value
        ? `/api/v1/catalogos/distritos?canton_id=${cantonSelect.value}`
        : "",
      "Sin distrito"
    );
  });

  syncClientTypeUI();
  tipoInputs.forEach((input) => input.addEventListener("change", syncClientTypeUI));
});
