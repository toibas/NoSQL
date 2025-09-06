/**
 * Lädt eine Logdatei hoch und zeigt das Ergebnis an.
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
 * Sucht Logs mit den angegebenen Filtern und zeigt die Ergebnisse an.
 * @returns {Promise<void>}
 */
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

  const res = await apiCall(`${API_BASE}/search?${params.toString()}`);
  showResult("searchResults", res.data.logs || res.data);
}

/**
 * Holt die Statistik der Log-Level und zeigt sie an.
 * @returns {Promise<void>}
 */
async function getStats() {
  const res = await apiCall(`${API_BASE}/stats/levels`);
  showResult("statsResult", res.data.levels || res.data);
}

/**
 * Lädt alle Logs (bis zu 1000) und zeigt sie an.
 * @returns {Promise<void>}
 */
async function loadAllLogs() {
  const res = await apiCall(`${API_BASE}/search?size=1000`);
  showResult("searchResults", res.data.logs || res.data);
}

/**
 * Holt die Timeline-Statistik (Logs pro Stunde und Level) und zeigt sie an.
 * @returns {Promise<void>}
 */
async function getTimeline() {
  const res = await apiCall(`${API_BASE}/stats/timeline`);
  const data = res.data.timeline || res.data;

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
 * Holt die Top-Komponenten mit ERROR-Logs und zeigt sie an.
 * @returns {Promise<void>}
 */
async function getTopErrorComponents() {
  const res = await apiCall(`${API_BASE}/stats/errors/components`);
  const data = res.data.top_error_components || res.data;

  if (!data.top_components?.buckets) {
    return showResult("topErrorComponentsResult", data);
  }

  const lines = data.top_components.buckets.map(b =>
    `${b.key}: ${b.doc_count}`
  );

  document.getElementById("topErrorComponentsResult").textContent = lines.join("\n");
}



