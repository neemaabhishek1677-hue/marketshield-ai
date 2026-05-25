export default function KpiCard({ label, value, delta, trend }) {
  const trendColor = trend === 'up' ? 'text-red-400' : trend === 'down' ? 'text-emerald-400' : 'text-slate-400'
  return (
    <div className="card">
      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
      {delta && <p className={`text-xs mt-1 ${trendColor}`}>{delta}</p>}
    </div>
  )
}
