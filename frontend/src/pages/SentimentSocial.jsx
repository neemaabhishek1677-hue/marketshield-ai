import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function SentimentSocial() {
  const [stocks, setStocks] = useState([])
  const [selected, setSelected] = useState('APEX')
  const [sentiment, setSentiment] = useState(null)
  const [pump, setPump] = useState(null)

  useEffect(() => {
    api.stocks().then((s) => {
      setStocks(s)
      if (s.length) setSelected(s.find((x) => x.ticker === 'APEX')?.ticker || s[0].ticker)
    })
  }, [])

  useEffect(() => {
    if (!selected) return
    Promise.all([api.stockSentiment(selected), api.stockPump(selected)]).then(([s, p]) => {
      setSentiment(s)
      setPump(p)
    })
  }, [selected])

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-bold text-white">Sentiment & Social Intelligence</h2>
      <div className="flex gap-2 flex-wrap">
        {stocks.map((s) => (
          <button
            key={s.ticker}
            onClick={() => setSelected(s.ticker)}
            className={`px-3 py-1 rounded font-mono text-sm ${
              selected === s.ticker ? 'bg-accent text-white' : 'bg-surface-card border border-slate-600'
            }`}
          >
            {s.ticker}
          </button>
        ))}
      </div>

      {!sentiment ? (
        <LoadingState />
      ) : (
        <>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300">News sentiment — {selected}</h3>
              <p className="text-2xl font-mono mt-2 text-accent-cyan">{sentiment.aggregate_score?.toFixed(3)}</p>
              <div className="mt-4 space-y-3 max-h-64 overflow-y-auto">
                {sentiment.articles?.map((a, i) => (
                  <div key={i} className="text-sm border-b border-slate-700/40 pb-2">
                    <p>{a.headline}</p>
                    <span className="text-xs text-slate-500">{a.label} · {a.tone}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300">Social manipulation risk</h3>
              {pump && (
                <>
                  <p className="text-lg text-amber-400 mt-2">{pump.risk_level}</p>
                  <p className="text-sm text-slate-400 mt-2">{pump.explanation}</p>
                  <Link to={`/stocks/${selected}`} className="text-accent text-sm mt-4 inline-block">Stock drill-down →</Link>
                </>
              )}
            </div>
          </div>
          <p className="text-xs text-slate-600">
            Social posts are simulated for demo. APEX scenario embeds coordinated hype bursts for pump-and-dump surveillance.
          </p>
        </>
      )}
    </div>
  )
}
