/* ============================================================
   ProPat — login.js
   Lógica exclusiva de la página de login
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  const form = document.getElementById('loginForm');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    ppAlert('#loginAlert', 'warning', 'Verificando...');

    const payload = {
      username: form.querySelector('[name="username"]').value.trim(),
      password: form.querySelector('[name="password"]').value,
    };

    try {
      const res  = await fetch('/api/v1/auth/verificar', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        ppAlert('#loginAlert', 'danger', data.error || 'Credenciales inválidas');
        return;
      }

      ppAlert('#loginAlert', 'success', '¡Acceso concedido! Redirigiendo...');
      setTimeout(() => { window.location.href = '/principal'; }, 600);

    } catch (err) {
      ppAlert('#loginAlert', 'danger', 'Error de conexión. Intenta de nuevo.');
    }
  });

});