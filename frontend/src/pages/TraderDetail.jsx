import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function TraderDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)

  useEffect(() => {
    api.trader(id).then(setData).catch(console.error)
  }, [id])

  if (!data) return <LoadingState />

  const ins = data.insight
  return (
    <div className="p-6 space-y-4">
      <Link to="/traders" className="text-sm text-accent">← Traders</Link>
      <h2 className="text-2xl font-bold font-mono text-white">{data.trader.external_id}</h2>
      <p className="text-slate-400">{data.trader.name}</p>
      <div className="card">
        <h3 className="font-semibold text-slate-300">Why flagged</h3>
        <ul className="mt-2 list-disc list-inside text-sm text-slate-400">
          {ins?.why_flagged?.map((w, i) => <li key={i}>{w}</li>)}
        </ul>
        <p className="mt-4 text-sm">{ins?.interaction}</p>
      </div>
      <div className="card">
        <h3 className="font-semibold text-slate-300">Suggested actions</h3>
        <div className="flex gap-2 mt-2">
          {ins?.suggested_actions?.map((a) => (
            <span key={a} className="px-2 py-1 rounded bg-accent/20 text-accent text-xs">{a}</span>
          ))}
        </div>
      </div>
      <Link to="/graph" className="text-accent text-sm">View insider network graph →</Link>
    </div>
  )
}
