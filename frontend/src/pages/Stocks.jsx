import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function Stocks() {
  const [stocks, setStocks] = useState([])

  useEffect(() => {
    api.stocks().then(setStocks).catch(console.error)
  }, [])

  if (!stocks.length) return <LoadingState />

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-white mb-4">Stock Surveillance</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stocks.map((s) => (
          <Link key={s.ticker} to={`/stocks/${s.ticker}`} className="card hover:border-accent/50 transition-colors">
            <div className="flex justify-between">
              <span className="font-mono text-lg text-accent-cyan">{s.ticker}</span>
              <span className="text-xs text-slate-500">{s.sector}</span>
            </div>
            <p className="text-sm text-slate-400 mt-1">{s.name}</p>
            <p className="text-xs text-slate-600 mt-2">Mkt cap ${(s.market_cap / 1e9).toFixed(2)}B</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
