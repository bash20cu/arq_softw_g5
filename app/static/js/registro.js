(function () {
  const form = document.getElementById("registerForm");
  const result = document.getElementById("resultadoRegistro");

  if (!form || !result) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const cedula = document.getElementById("cedula").value.trim();
    const nombre = document.getElementById("nombre").value.trim();
    const apellido = document.getElementById("apellido").value.trim();
    const email = document.getElementById("email").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
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
