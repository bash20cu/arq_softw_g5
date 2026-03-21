function filtrarOrdenes(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-ordenes tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}
