function filtrar(query) {
  const value = query.toLowerCase();
  document.querySelectorAll("#tabla-usuarios tbody tr").forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
  });
}
