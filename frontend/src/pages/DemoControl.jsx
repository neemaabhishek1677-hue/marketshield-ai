import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { Play, Database, Cpu } from 'lucide-react'

export default function DemoControl() {
  const [scenarios, setScenarios] = useState([])
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.scenarios().then(setScenarios).catch(console.error)
    api.health().then(setHealth).catch(() => setHealth({ database: 'unknown' }))
  }, [])

  const seed = async () => {
    setLoading(true)
    setStatus('Generating synthetic market surveillance dataset...')
    try {
      const res = await api.seed(30)
      setStatus(`Done: ${res.trades} trades, ${res.alerts} alerts, scenarios: ${res.scenarios_embedded.join(', ')}`)
    } catch (e) {
      setStatus(`Error: ${e.message}`)
    }
    setLoading(false)
  }

  const retrain = async () => {
    setLoading(true)
    try {
      const res = await api.retrain()
      setStatus(`ML retrain: ${res.message}`)
    } catch (e) {
      setStatus(e.message)
    }
    setLoading(false)
  }

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <h2 className="text-xl font-bold text-white">Demo Scenario Control Panel</h2>
      <p className="text-sm text-slate-400">
        Seed embedded surveillance scenarios for judge walkthrough. All data is synthetic — not real market or PII.
      </p>

      <div className="flex gap-4">
        <button onClick={seed} disabled={loading} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent hover:bg-blue-600 text-white disabled:opacity-50">
          <Database className="w-4 h-4" /> Generate demo data
        </button>
        <button onClick={retrain} disabled={loading} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-600 hover:border-accent">
          <Cpu className="w-4 h-4" /> Retrain ML models
        </button>
      </div>

      {status && <p className="text-sm text-accent-cyan font-mono p-3 bg-surface-card rounded">{status}</p>}
      {health && <p className="text-xs text-slate-500">API: {health.status} · DB: {health.database}</p>}

      <div className="space-y-4">
        {scenarios.map((s) => (
          <div key={s.id} className="card">
            <div className="flex items-start gap-3">
              <Play className="w-5 h-5 text-accent-cyan shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-white">{s.name}</h3>
                <p className="text-sm text-slate-400 mt-1">{s.description}</p>
                <p className="text-xs text-slate-600 mt-2 font-mono">tag: {s.scenario_tag}</p>
                <ol className="mt-3 list-decimal list-inside text-sm text-slate-500 space-y-1">
                  {s.walkthrough?.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
