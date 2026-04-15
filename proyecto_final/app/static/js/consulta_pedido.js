/* ProPat — consulta_pedido.js */

document.addEventListener('DOMContentLoaded', () => {
  const form   = document.getElementById('statusForm');
  const result = document.getElementById('statusResult');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const orderId = form.querySelector('[name="order_id"]').value;

    ppAlertClear('#statusAlert');
    result.classList.remove('open');

    const res  = await fetch(`/api/v1/ordenes/${orderId}/estado`);
    const data = await res.json();

    if (!res.ok) {
      ppAlert('#statusAlert', 'danger', data.error || 'No se encontró la orden');
      return;
    }

    // Rellenar resultado
    document.getElementById('resId').textContent     = `#${data.id_orden}`;
    document.getElementById('resFecha').textContent  =
      data.fecha_orden ? `Fecha: ${ppDate(data.fecha_orden)}` : '';
    document.getElementById('resEstado').textContent = data.estado;
    document.getElementById('resBadge').innerHTML    = ppOrderBadge(data.estado);
    document.getElementById('resTotal').textContent  = ppPrice(data.total);

    result.classList.add('open');
  });
});