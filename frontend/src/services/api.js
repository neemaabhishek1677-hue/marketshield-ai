const BASE = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}/api/v1${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || res.statusText)
  }
  return res.json()
}

export const api = {
  health: () => request('/health'),
  seed: (days = 30) => request('/seed/generate-demo-data', { method: 'POST', body: JSON.stringify({ days }) }),
  dashboard: () => request('/dashboard/overview'),
  heatmap: () => request('/dashboard/market-heatmap'),
  alerts: (params = '') => request(`/alerts${params}`),
  alert: (id) => request(`/alerts/${id}`),
  patchAlert: (id, status) => request(`/alerts/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  stocks: () => request('/stocks'),
  stock: (ticker) => request(`/stocks/${ticker}`),
  stockRisk: (ticker) => request(`/stocks/${ticker}/risk`),
  stockSentiment: (ticker) => request(`/stocks/${ticker}/sentiment`),
  stockPump: (ticker) => request(`/stocks/${ticker}/pump-dump-prediction`),
  traders: () => request('/traders'),
  trader: (id) => request(`/traders/${id}`),
  traderGraph: (id) => request(`/traders/${id}/graph`),
  graph: () => request('/graphs/insider-network'),
  scenarios: () => request('/demo/scenarios'),
  topSuspicious: () => request('/analytics/top-suspicious'),
  events: () => request('/events'),
  retrain: () => request('/ml/retrain', { method: 'POST' }),
}

export function severityBadge(sev) {
  const m = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' }
  return m[sev] || 'badge-medium'
}
