async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (data.success) {
    document.getElementById("authResult").textContent =
      "Benutzer erfolgreich registriert. Bitte logge dich jetzt ein.";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
  } else {
    document.getElementById("authResult").textContent =
      data.error || "Registrierung fehlgeschlagen";
  }
}

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  document.getElementById("authResult").textContent =
    data.message || data.error || "Login abgeschlossen";

  if (data.success) {
    localStorage.setItem("loggedIn", "true");
    window.location.href = "main.html";
  }
}