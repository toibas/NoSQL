/**
 * Führt einen API-Call mit fetch aus.
 * @param {string} url - Die URL der API.
 * @param {string} [method='GET'] - HTTP-Methode (GET, POST, etc.).
 * @param {object|FormData|null} [data=null] - Daten für den Request-Body.
 * @param {object} [headers={}] - Zusätzliche Header.
 * @returns {Promise<object>} Ein Objekt mit { success, data, status } oder { success, error }.
 */
async function apiCall(url, method = 'GET', data = null, headers = {}) {
  try {
    const options = { method, headers: { ...headers } };

    if (data) {
      if (data instanceof FormData) {
        options.body = data;
      } else {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
      }
    }

    const response = await fetch(url, options);
    const result = await response.json();

    return { success: response.ok, data: result, status: response.status };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Zeigt das Ergebnis in einem HTML-Element an.
 * @param {string} elementId - Die ID des Elements.
 * @param {any} result - Das anzuzeigende Ergebnis.
 * @returns {void} Es wird nichts zurückgegeben, das Ergebnis wird angezeigt.
 */
function showResult(elementId, result) {
  const element = document.getElementById(elementId);
  if (!element) return;
  if (typeof result === "string") {
    element.textContent = result;
  } else {
    element.textContent = JSON.stringify(result, null, 2);
  }
}