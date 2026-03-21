function currency(value) {
  return `Q ${value.toFixed(2)}`;
}

function actualizarResumenOrden() {
  let total = 0;
  document.querySelectorAll(".linea-orden").forEach((linea) => {
    const select = linea.querySelector(".producto-select");
    const cantidadInput = linea.querySelector(".cantidad-input");
    const subtotalInput = linea.querySelector(".subtotal-linea");
    const precio = Number(select?.selectedOptions?.[0]?.dataset?.precio || 0);
    const cantidad = Number(cantidadInput?.value || 0);
    const subtotal = precio * cantidad;
    total += subtotal;
    if (subtotalInput) {
      subtotalInput.value = currency(subtotal);
    }
  });

  const totalLabel = document.getElementById("ordenTotal");
  if (totalLabel) {
    totalLabel.textContent = currency(total);
  }
}

function agregarLineaOrden() {
  const template = document.getElementById("lineaOrdenTemplate");
  const container = document.getElementById("lineasOrden");
  if (!template || !container) {
    return;
  }

  container.insertAdjacentHTML("beforeend", template.innerHTML);
  actualizarResumenOrden();
}

function eliminarLineaOrden(button) {
  const lineas = document.querySelectorAll(".linea-orden");
  if (lineas.length === 1) {
    lineas[0].querySelector(".producto-select").value = "";
    lineas[0].querySelector(".cantidad-input").value = 1;
    actualizarResumenOrden();
    return;
  }

  button.closest(".linea-orden")?.remove();
  actualizarResumenOrden();
}

document.addEventListener("DOMContentLoaded", actualizarResumenOrden);
