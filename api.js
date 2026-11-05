const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`API ${response.status}: ${detail || response.statusText}`)
  }
  return response.json()
}

export const api = {
  health: () => request('/health'),
  overview: () => request('/api/overview'),
  engines: (params = {}) => {
    const query = new URLSearchParams(params)
    return request(`/api/engines?${query.toString()}`)
  },
  engine: (id) => request(`/api/engines/${encodeURIComponent(id)}`),
  metrics: () => request('/api/model/metrics'),
}
