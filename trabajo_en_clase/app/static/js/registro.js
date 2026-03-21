(function () {
  const form = document.getElementById("registerForm");
  const result = document.getElementById("resultadoRegistro");
  const provinciaSelect = document.getElementById("provinciaReg");
  const cantonSelect = document.getElementById("cantonReg");
  const distritoSelect = document.getElementById("distritoReg");

  if (!form || !result) {
    return;
  }

  const loadOptions = async (url, select, placeholder) => {
    select.innerHTML = `<option value="">${placeholder}</option>`;
    const response = await fetch(url);
    const data = await response.json();
    data.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id_provincia || item.id_canton || item.id_distrito;
      option.textContent = item.nombre;
      select.appendChild(option);
    });
  };

  const resetSelect = (select, placeholder) => {
    select.innerHTML = `<option value="">${placeholder}</option>`;
  };

  if (provinciaSelect && cantonSelect && distritoSelect) {
    fetch("/api/v1/catalogos/provincias", { credentials: "same-origin" })
      .then((response) => response.json())
      .then((data) => {
        provinciaSelect.innerHTML = '<option value="">Seleccionar provincia...</option>';
        data.forEach((item) => {
          const option = document.createElement("option");
          option.value = item.id_provincia;
          option.textContent = item.nombre;
          provinciaSelect.appendChild(option);
        });
      });

    provinciaSelect.addEventListener("change", async () => {
      resetSelect(cantonSelect, "Seleccionar canton...");
      resetSelect(distritoSelect, "Seleccionar distrito...");
      if (!provinciaSelect.value) {
        return;
      }
      await loadOptions(
        `/api/v1/catalogos/cantones?provincia_id=${provinciaSelect.value}`,
        cantonSelect,
        "Seleccionar canton..."
      );
    });

    cantonSelect.addEventListener("change", async () => {
      resetSelect(distritoSelect, "Seleccionar distrito...");
      if (!cantonSelect.value) {
        return;
      }
      await loadOptions(
        `/api/v1/catalogos/distritos?canton_id=${cantonSelect.value}`,
        distritoSelect,
        "Seleccionar distrito..."
      );
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const cedula = document.getElementById("cedula").value.trim();
    const nombre = document.getElementById("nombre").value.trim();
    const apellido = document.getElementById("apellido").value.trim();
    const email = document.getElementById("email").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
    const id_distrito = distritoSelect ? distritoSelect.value : "";
    const username = document.getElementById("usernameReg").value.trim();
    const password = document.getElementById("passwordReg").value;

    try {
      const response = await fetch("/api/v1/auth/registro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cedula_persona: cedula,
          nombre,
          apellido,
          email,
          telefono,
          id_distrito: id_distrito || null,
          username,
          password,
          activo: true,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        result.className = "mt-3 text-danger";
        result.textContent = `Error: ${data.error || "No autorizado o datos invalidos"}`;
        return;
      }

      result.className = "mt-3 text-success";
      result.textContent = `Usuario ${data.username || username} creado. Iniciando sesion...`;

      const loginResponse = await fetch("/api/v1/auth/verificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (loginResponse.ok) {
        window.location.href = "/principal";
        return;
      }

      form.reset();
    } catch (_) {
      result.className = "mt-3 text-danger";
      result.textContent = "Error de red. Intenta nuevamente.";
    }
  });
})();
