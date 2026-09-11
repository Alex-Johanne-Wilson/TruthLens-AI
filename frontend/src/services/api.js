/**
 * TruthLens Cyber-Forensics API Service
 * Supports both direct communication with http://127.0.0.1:8000 and Vite reverse proxy
 */

const BACKEND_URL = 'http://127.0.0.1:8000';

export async function checkBackendHealth() {
  // Try direct first, then relative proxy if needed
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (response.ok) {
      const data = await response.json();
      return { ok: true, status: response.status, data };
    }
  } catch (e) {
    // Try proxy fallback
    try {
      const response = await fetch('/health', {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (response.ok) {
        const data = await response.json();
        return { ok: true, status: response.status, data };
      }
    } catch (proxyError) {
      return { ok: false, error: proxyError.message, data: null };
    }
  }
  return { ok: false, status: 500, data: null };
}

export async function analyzeImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  let response;
  try {
    response = await fetch(`${BACKEND_URL}/api/analyze/image`, {
      method: 'POST',
      body: formData,
    });
  } catch (directErr) {
    // Retry with Vite proxy
    response = await fetch('/api/analyze/image', {
      method: 'POST',
      body: formData,
    });
  }

  if (!response.ok) {
    let errorDetail = 'Analysis request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return await response.json();
}

export async function analyzeDeepfake(file) {
  const formData = new FormData();
  formData.append('file', file);

  let response;
  try {
    response = await fetch(`${BACKEND_URL}/api/analyze/deepfake`, {
      method: 'POST',
      body: formData,
    });
  } catch (directErr) {
    response = await fetch('/api/analyze/deepfake', {
      method: 'POST',
      body: formData,
    });
  }

  if (!response.ok) {
    let errorDetail = 'Deepfake analysis failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return await response.json();
}

export function resolveGradcamUrl(path) {
  if (!path) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${BACKEND_URL}${cleanPath}`;
}
