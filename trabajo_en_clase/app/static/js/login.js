(function () {
  const form = document.getElementById("loginForm");
  const result = document.getElementById("resultadoLogin");

  if (!form || !result) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    result.className = "mt-3 text-muted";
    result.textContent = "Validando credenciales...";

    try {
      const response = await fetch("/api/v1/auth/verificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        result.className = "mt-3 text-danger";
        result.textContent = `Error: ${data.error || "Credenciales invalidas"}`;
        return;
      }

      result.className = "mt-3 text-success";
      result.textContent = `Bienvenido, ${data.user.username}. Redirigiendo...`;

      const nextRoute = data.next === "/api/v1/menu/principal" ? "/principal" : data.next;
      window.location.href = nextRoute || "/principal";
    } catch (_) {
      result.className = "mt-3 text-danger";
      result.textContent = "Error de red. Intenta nuevamente.";
    }
  });
})();
