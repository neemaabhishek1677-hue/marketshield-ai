import { useEffect, useState } from 'react'
import { api, severityBadge } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [selected, setSelected] = useState(null)
  const [filter, setFilter] = useState('')

  const load = () => api.alerts(filter ? `?status=${filter}` : '').then(setAlerts)

  useEffect(() => { load().catch(console.error) }, [filter])

  const openDetail = async (id) => {
    const d = await api.alert(id)
    setSelected(d)
  }

  const updateStatus = async (id, status) => {
    await api.patchAlert(id, status)
    load()
    if (selected?.id === id) setSelected({ ...selected, status })
  }

  if (!alerts.length && !selected) return <div className="p-6"><LoadingState /></div>

  return (
    <div className="p-6 flex gap-4 h-[calc(100vh-2rem)]">
      <div className="flex-1 card overflow-hidden flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Risk Alert Queue</h2>
          <select value={filter} onChange={(e) => setFilter(e.target.value)} className="bg-surface border border-slate-600 rounded px-2 py-1 text-sm">
            <option value="">All statuses</option>
            <option value="new">New</option>
            <option value="under_review">Under review</option>
            <option value="escalated">Escalated</option>
            <option value="dismissed">Dismissed</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
        <div className="overflow-y-auto flex-1 space-y-2">
          {alerts.map((a) => (
            <button
              key={a.id}
              onClick={() => openDetail(a.id)}
              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                selected?.id === a.id ? 'border-accent bg-accent/10' : 'border-slate-700/50 hover:border-slate-500'
              }`}
            >
              <div className="flex justify-between">
                <span className="font-medium text-sm">{a.title}</span>
                <span className={severityBadge(a.severity)}>{a.severity}</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{a.alert_type} · confidence {(a.confidence * 100).toFixed(0)}%</p>
            </button>
          ))}
        </div>
      </div>
      {selected && (
        <div className="w-96 card overflow-y-auto">
          <h3 className="font-bold text-white">{selected.title}</h3>
          <p className="text-xs text-slate-500 mt-1">{selected.ticker} · {selected.trader_external_id}</p>
          <p className="text-sm text-slate-300 mt-4 leading-relaxed">{selected.explanation}</p>
          <div className="mt-4">
            <h4 className="text-xs text-slate-500 uppercase">Top drivers</h4>
            <ul className="mt-2 space-y-1 text-sm">
              {(selected.drivers_parsed || []).map((d, i) => (
                <li key={i} className="text-slate-400">• {d.description} ({d.contribution})</li>
              ))}
            </ul>
          </div>
          <p className="text-xs text-accent mt-4">Suggested: {selected.suggested_action}</p>
          <div className="flex flex-wrap gap-2 mt-4">
            {['under_review', 'escalated', 'dismissed', 'resolved'].map((s) => (
              <button key={s} onClick={() => updateStatus(selected.id, s)} className="text-xs px-2 py-1 rounded bg-surface-light border border-slate-600 hover:border-accent">
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
