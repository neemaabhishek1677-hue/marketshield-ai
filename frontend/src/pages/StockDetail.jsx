import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function StockDetail() {
  const { ticker } = useParams()
  const [data, setData] = useState(null)
  const [risk, setRisk] = useState(null)
  const [pump, setPump] = useState(null)
  const [sentiment, setSentiment] = useState(null)

  useEffect(() => {
    Promise.all([
      api.stock(ticker),
      api.stockRisk(ticker).catch(() => null),
      api.stockPump(ticker).catch(() => null),
      api.stockSentiment(ticker).catch(() => null),
    ]).then(([d, r, p, s]) => {
      setData(d)
      setRisk(r)
      setPump(p)
      setSentiment(s)
    })
  }, [ticker])

  if (!data) return <LoadingState />

  return (
    <div className="p-6 space-y-6">
      <Link to="/stocks" className="text-sm text-accent">← Stocks</Link>
      <header>
        <h2 className="text-2xl font-bold text-white font-mono">{data.stock.ticker}</h2>
        <p className="text-slate-400">{data.stock.name} · {data.stock.sector}</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-xs text-slate-500">Unified risk</p>
          <p className="text-3xl font-bold text-red-400">{((risk?.unified_score || 0) * 100).toFixed(0)}%</p>
        </div>
        <div className="card">
          <p className="text-xs text-slate-500">Pump-and-dump level</p>
          <p className="text-lg font-semibold text-amber-400">{pump?.risk_level || '—'}</p>
        </div>
        <div className="card">
          <p className="text-xs text-slate-500">Sentiment aggregate</p>
          <p className="text-lg font-mono">{sentiment?.aggregate_score?.toFixed(2) || '—'}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-slate-300 mb-2">Analyst insight</h3>
        <p className="text-sm text-slate-400">{data.insight?.summary}</p>
        <ul className="mt-2 list-disc list-inside text-sm text-slate-500">
          {data.insight?.why_risky?.map((w, i) => <li key={i}>{w}</li>)}
        </ul>
      </div>

      {pump && (
        <div className="card">
          <h3 className="font-semibold text-slate-300 mb-2">Pump-and-dump prediction</h3>
          <p className="text-sm">{pump.explanation}</p>
          <pre className="mt-2 text-xs font-mono text-slate-500">{JSON.stringify(pump.indicators, null, 2)}</pre>
        </div>
      )}

      <div className="card">
        <h3 className="font-semibold text-slate-300 mb-2">News sentiment</h3>
        {sentiment?.articles?.map((a, i) => (
          <div key={i} className="py-2 border-b border-slate-700/30 text-sm">
            <p>{a.headline}</p>
            <p className="text-xs text-slate-500">{a.label} · {a.tone} · hype {a.hype_score}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
