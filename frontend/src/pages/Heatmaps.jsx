import { useEffect, useState } from 'react'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

function HeatGrid({ title, cells }) {
  const max = Math.max(...cells.map((c) => c.value), 0.01)
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">{title}</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {cells.map((c, i) => {
          const intensity = c.value / max
          const bg = `rgba(59, 130, 246, ${0.15 + intensity * 0.85})`
          return (
            <div
              key={i}
              className="p-3 rounded border border-slate-700/50 text-center"
              style={{ background: bg }}
              title={`${c.row} / ${c.col}: ${c.value}`}
            >
              <p className="font-mono text-xs text-white">{c.col || c.row}</p>
              <p className="text-lg font-bold">{(c.value * 100).toFixed(0)}%</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Heatmaps() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.heatmap().then(setData).catch(console.error)
  }, [])

  if (!data) return <div className="p-6"><LoadingState /></div>

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-bold text-white">Financial Intelligence Heatmaps</h2>
      <HeatGrid title="Sector-level risk" cells={data.sector_risk} />
      <HeatGrid title="Stock-level risk" cells={data.stock_risk} />
      <HeatGrid title="Event-window abnormality" cells={data.event_window} />
      <HeatGrid title="Sentiment bursts" cells={data.sentiment_burst} />
      <HeatGrid title="Social coordination" cells={data.social_coordination} />
    </div>
  )
}
