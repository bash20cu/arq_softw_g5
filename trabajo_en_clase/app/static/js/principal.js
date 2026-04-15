(async function () {
  const welcome = document.getElementById("principalWelcome");
  const kpiOrdenes = document.getElementById("kpiOrdenes");
  const kpiEnvios = document.getElementById("kpiEnvios");
  const kpiSoporte = document.getElementById("kpiSoporte");
  const modulos = document.getElementById("principalModulos");
  const estado = document.getElementById("principalEstado");

  const setStatus = (text, kind) => {
    estado.className = `alert alert-${kind}`;
    estado.textContent = text;
  };

  const renderModulos = (items) => {
    modulos.innerHTML = "";
    items.forEach((item) => {
      const col = document.createElement("div");
      col.className = "col-md-6 col-lg-3";
      col.innerHTML = `
        <div class="card modulo-card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">${item.nombre}</h5>
            <p class="card-text text-muted">${item.descripcion}</p>
            <a href="${item.ruta_front}" class="btn btn-outline-primary btn-sm">Abrir modulo</a>
          </div>
        </div>
      `;
      modulos.appendChild(col);
    });
  };

  try {
    const response = await fetch("/api/v1/menu/principal");
    const data = await response.json();

    if (!response.ok) {
      setStatus(data.error || "Sesion expirada. Inicia sesion nuevamente.", "warning");
      setTimeout(() => {
        window.location.href = "/login";
      }, 1200);
      return;
    }

    welcome.textContent = data.bienvenida || "Bienvenido";
    kpiOrdenes.textContent = data.kpis.ordenes_pendientes;
    kpiEnvios.textContent = data.kpis.envios_en_ruta;
    kpiSoporte.textContent = data.kpis.casos_soporte_abiertos;
    renderModulos(data.modulos || []);
    setStatus("Menu cargado correctamente.", "success");
  } catch (_) {
    setStatus("No se pudo cargar el menu principal.", "danger");
  }
})();
