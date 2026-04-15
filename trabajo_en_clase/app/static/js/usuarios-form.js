function togglePwd() {
  const input = document.getElementById("inputPassword");
  const icon = document.getElementById("eye-icon");

  if (!input || !icon) {
    return;
  }

  if (input.type === "password") {
    input.type = "text";
    icon.className = "bi bi-eye-slash";
    return;
  }

  input.type = "password";
  icon.className = "bi bi-eye";
}
