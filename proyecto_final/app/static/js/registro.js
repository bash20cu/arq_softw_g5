/* ProPat — registro.js */

document.addEventListener('DOMContentLoaded', () => {
  // Carga provincias y enlaza los tres dropdowns de ubicación
  ppLoadProvincias('regProvincia');
  ppBindLocation('regProvincia', 'regCanton', 'regDistrito');

  const form = document.getElementById('registerForm');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    ppAlert('#registerAlert', 'warning', 'Registrando...');

    const payload = {
      cedula_persona: form.querySelector('[name="cedula_persona"]').value.trim(),
      telefono:       form.querySelector('[name="telefono"]').value.trim() || null,
      nombre:         form.querySelector('[name="nombre"]').value.trim(),
      apellido:       form.querySelector('[name="apellido"]').value.trim(),
      email:          form.querySelector('[name="email"]').value.trim(),
      direccion:      form.querySelector('[name="direccion"]').value.trim() || null,
      username:       form.querySelector('[name="username"]').value.trim(),
      password:       form.querySelector('[name="password"]').value,
      id_distrito:    Number(document.getElementById('regDistrito').value) || null,
      activo:         true,
    };

    const res  = await fetch('/api/v1/auth/registro', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      ppAlert('#registerAlert', 'danger', data.error || 'No fue posible registrar');
      return;
    }

    ppAlert('#registerAlert', 'success', '¡Cuenta creada! Redirigiendo al login...');
    form.reset();
    setTimeout(() => { window.location.href = '/login'; }, 1500);
  });
});