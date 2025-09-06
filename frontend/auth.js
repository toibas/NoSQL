/**
 * Registriert einen neuen Benutzer über die API und zeigt das Ergebnis an.
 * @returns {Promise<void>} Es wird nichts zurückgegeben, das Ergebnis wird angezeigt.
 */
async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await apiCall(`${API_BASE}/register`, "POST", { username, password });

  if (res.success) {
    document.getElementById("authResult").textContent =
      "Benutzer erfolgreich registriert. Bitte logge dich jetzt ein.";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
  } else {
    document.getElementById("authResult").textContent =
      res.data?.error || "Registrierung fehlgeschlagen";
  }
}

/**
 * Loggt einen Benutzer über die API ein und leitet ggf. weiter.
 * @returns {Promise<void>} Es wird nichts zurückgegeben, das Ergebnis wird angezeigt oder weitergeleitet.
 */
async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await apiCall(`${API_BASE}/login`, "POST", { username, password });

  document.getElementById("authResult").textContent =
    res.data?.message || res.data?.error || "Login abgeschlossen";

  if (res.success) {
    localStorage.setItem("loggedIn", "true");
    window.location.href = "main.html";
  }
}
