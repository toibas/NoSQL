

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
