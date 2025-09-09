/**
 * Registriert einen neuen Benutzer.
 * @returns {Promise<void>} Es wird nichts zurückgegeben, das Ergebnis wird angezeigt.
 */
async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const result = await apiCall(`${API_BASE}/register`, "POST", { username, password });

  if (result.success) {
    document.getElementById("authResult").textContent =
      "Benutzer erfolgreich registriert. Bitte logge dich jetzt ein.";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
  } else {
    document.getElementById("authResult").textContent =
      result.data?.error || "Registrierung fehlgeschlagen";
  }
}

/**
 * Loggt einen Benutzer ein und leitet ggf. weiter.
 * @returns {Promise<void>} Es wird nichts zurückgegeben, das Ergebnis wird angezeigt oder weitergeleitet.
 */
async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const result = await apiCall(`${API_BASE}/login`, "POST", { username, password });

  document.getElementById("authResult").textContent =
    result.data?.message || result.data?.error || "Login abgeschlossen";

  if (result.success) {
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("userId", result.data.id);
    localStorage.setItem("username", result.data.username);
    window.location.href = "main.html";
  }
}


