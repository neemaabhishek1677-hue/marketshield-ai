import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { api } from '../services/api'
import KpiCard from '../components/KpiCard'
import SeverityBadge from '../components/SeverityBadge'
import LoadingState from '../components/LoadingState'
import EmptyState from '../components/EmptyState'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="p-6 text-red-400">API error: {error}. Start backend & seed demo data.</div>
  if (!data) return <LoadingState />

  const anomalyData = data.anomaly_timeseries?.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit' }),
    value: p.value,
  }))

  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-white">Market Surveillance Dashboard</h2>
          <p className="text-sm text-slate-500 mt-1">{data.disclaimer}</p>
        </div>
        <div className="text-right text-xs text-slate-500 font-mono">
          LIVE DESK · {new Date().toLocaleString()}
        </div>
      </header>

      {data.kpis?.length === 0 ? (
        <EmptyState title="No surveillance data" action={<Link to="/demo" className="text-accent mt-4 inline-block">Go to Demo Control →</Link>} />
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {data.kpis.map((k) => (
              <KpiCard key={k.label} {...k} />
            ))}
          </div>

          <div className="grid lg:grid-cols-3 gap-4">
            <div className="card lg:col-span-2">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Anomaly Detection Timeline</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={anomalyData}>
                  <defs>
                    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip contentStyle={{ background: '#151d28', border: '1px solid #334155' }} />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="url(#g)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Graph Risk Summary</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between"><span>Clusters</span><span className="font-mono text-accent-cyan">{data.graph_summary?.clusters}</span></li>
                <li className="flex justify-between"><span>Suspicious edges</span><span className="font-mono text-amber-400">{data.graph_summary?.suspicious_edges}</span></li>
                <li className="flex justify-between"><span>Insider paths</span><span className="font-mono text-red-400">{data.graph_summary?.insider_paths}</span></li>
              </ul>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Top Risk Tickers</h3>
              <table className="w-full text-sm">
                <thead className="text-slate-500 text-xs">
                  <tr><th className="text-left py-1">Ticker</th><th>Sector</th><th>Risk</th><th>Pump</th></tr>
                </thead>
                <tbody>
                  {data.top_risk_tickers?.map((r) => (
                    <tr key={r.ticker} className="border-t border-slate-700/30">
                      <td className="py-2"><Link to={`/stocks/${r.ticker}`} className="text-accent-cyan hover:underline font-mono">{r.ticker}</Link></td>
                      <td className="text-slate-400">{r.sector}</td>
                      <td className="font-mono">{(r.unified_score * 100).toFixed(0)}%</td>
                      <td className="text-xs text-amber-400">{r.pump_risk}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">High-Risk Traders</h3>
              <table className="w-full text-sm">
                <thead className="text-slate-500 text-xs">
                  <tr><th className="text-left">ID</th><th>Score</th><th>Alerts</th></tr>
                </thead>
                <tbody>
                  {data.high_risk_traders?.map((t) => (
                    <tr key={t.external_id} className="border-t border-slate-700/30">
                      <td className="py-2"><Link to={`/traders/${t.external_id}`} className="text-accent-cyan font-mono">{t.external_id}</Link></td>
                      <td className="font-mono">{(t.risk_score * 100).toFixed(0)}%</td>
                      <td>{t.alert_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Sector Risk Heatmap</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={data.sector_heatmap?.map((c) => ({ name: c.col, risk: c.value }))}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} domain={[0, 1]} />
                  <Tooltip contentStyle={{ background: '#151d28', border: '1px solid #334155' }} />
                  <Bar dataKey="risk" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Alert Feed</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {data.recent_alerts?.map((a) => (
                  <Link key={a.id} to="/alerts" className="block p-2 rounded bg-surface/50 hover:bg-surface-light border border-slate-700/30">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-200 truncate">{a.title}</span>
                      <SeverityBadge severity={a.severity} />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-sm font-semibold text-slate-300 mb-2">Pump-and-Dump Watchlist</h3>
            <div className="flex flex-wrap gap-2">
              {data.pump_watchlist?.map((p) => (
                <Link key={p.ticker} to={`/stocks/${p.ticker}`} className="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-sm font-mono">
                  {p.ticker} · {p.pump_risk}
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
