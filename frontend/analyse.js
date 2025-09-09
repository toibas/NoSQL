/**
 * Lädt eine Logdatei hoch.
 * @returns {Promise<void>}
 */
async function uploadLog() {
  const file = document.getElementById('logfileInput')?.files[0];
  if (!file) return alert("Bitte Datei auswählen");

  const formData = new FormData();
  formData.append("logfile", file);

  const res = await apiCall(`${API_BASE}/upload-log`, "POST", formData);
  showResult("uploadResult", res.data.message || res.data.error || res.data);
}

/**
 * Sucht Logs mit den angegebenen Filtern.
 * @returns {Promise<void>}
 */
async function searchLogs() {
  const params = new URLSearchParams();
  const searchQuery = document.getElementById("searchQuery").value;
  const levelFilter = document.getElementById("levelFilter").value;
  const componentFilter = document.getElementById("componentFilter").value;
  const timeFilter = document.getElementById("timeFilter").value;

  if (searchQuery) params.append("q", searchQuery);
  if (levelFilter) params.append("level", levelFilter);
  if (componentFilter) params.append("component", componentFilter);
  if (timeFilter) params.append("from_time", timeFilter);

  const result = await apiCall(`${API_BASE}/search?${params.toString()}`);
  showResult("searchResults", result.data.logs || result.data);
}

/**
 * Holt die Statistik der Log-Level.
 * @returns {Promise<void>}
 */
async function getStats() {
  const result = await apiCall(`${API_BASE}/stats/levels`);
  showResult("statsResult", result.data.levels || result.data);
}

/**
 * Lädt alle Logs (bis zu 1000).
 * @returns {Promise<void>}
 */
async function loadAllLogs() {
  const result = await apiCall(`${API_BASE}/search?size=1000`);
  showResult("searchResults", result.data.logs || result.data);
}

/**
 * Holt die Timeline-Statistik (Logs pro Stunde und Level).
 * @returns {Promise<void>}
 */
async function getTimeline() {
  const result = await apiCall(`${API_BASE}/stats/timeline`);
  const data = result.data.timeline || result.data;

  if (!data.logs_over_time?.buckets) {
    return showResult("timelineResult", data);
  }

  const lines = data.logs_over_time.buckets.map(bucket => {
    const time = bucket.key_as_string || bucket.key;
    const levels = bucket.levels?.buckets || [];
    const levelCounts = levels.map(l => `${l.key}: ${l.doc_count}`).join(", ");
    return `${time} → ${levelCounts}`;
  });

  document.getElementById("timelineResult").textContent = lines.join("\n");
}

/**
 * Holt die Top-Komponenten mit ERROR-Logs.
 * @returns {Promise<void>}
 */
async function getTopErrorComponents() {
  const result = await apiCall(`${API_BASE}/stats/errors/components`);
  const data = result.data.top_error_components || result.data;

  if (!data.top_components?.buckets) {
    return showResult("topErrorComponentsResult", data);
  }

  const lines = data.top_components.buckets.map(b =>
    `${b.key}: ${b.doc_count}`
  );

  document.getElementById("topErrorComponentsResult").textContent = lines.join("\n");
}




