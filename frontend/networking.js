async function apiCall(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        return { success: response.ok, data: result, status: response.status };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function showResult(elementId, result) {
    const element = document.getElementById(elementId);
    element.style.display = 'block';
    element.textContent = JSON.stringify(result, null, 2);
}

async function testAPI() {
    const result = await apiCall(`${API_BASE}/`);
    showResult('testResult', result);
}

async function testDatabase() {
    const result = await apiCall(`${API_BASE}/test`);
    showResult('testResult', result);
}


function showResult(id, result) {
  const el = document.getElementById(id);
  el.textContent = typeof result === "string"
    ? result
    : JSON.stringify(result, null, 2);
}

async function uploadLog() {
  const file = document.getElementById('logfileInput').files[0];
  if (!file) return alert("Bitte Datei auswählen");

  const formData = new FormData();
  formData.append("logfile", file);

  try {
    const res = await fetch(`${API_BASE}/upload-log`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    showResult("uploadResult", data.message || data.error || data);
  } catch (err) {
    showResult("uploadResult", "Fehler beim Upload");
  }
}


async function searchLogs() {
  const params = new URLSearchParams();
  const q = document.getElementById("searchQuery").value;
  const level = document.getElementById("levelFilter").value;
  const comp = document.getElementById("componentFilter").value;
  const time = document.getElementById("timeFilter").value;

  if (q) params.append("q", q);
  if (level) params.append("level", level);
  if (comp) params.append("component", comp);
  if (time) params.append("from_time", time);

  try {
    const res = await fetch(`${API_BASE}/search?${params.toString()}`);
    const data = await res.json();
    showResult("searchResults", data.logs || data);
  } catch (err) {
    showResult("searchResults", "Fehler bei der Suche");
  }
}


async function getStats() {
  try {
    const res = await fetch(`${API_BASE}/stats/levels`);
    const data = await res.json();
    showResult("statsResult", data.levels || data);
  } catch (err) {
    showResult("statsResult", "Fehler beim Abrufen der Statistik");
  }
}


async function loadAllLogs() {
  try {
    const res = await fetch(`${API_BASE}/search?size=1000`);
    const data = await res.json();
    showResult("searchResults", data.logs || data);
  } catch (err) {
    showResult("searchResults", "Fehler beim Laden der Logs");
  }
}
