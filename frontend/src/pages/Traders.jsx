import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

export default function Traders() {
  const [traders, setTraders] = useState([])

  useEffect(() => {
    api.traders().then(setTraders).catch(console.error)
  }, [])

  if (!traders.length) return <LoadingState />

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-white mb-4">Trader Investigation</h2>
      <table className="w-full card text-sm">
        <thead className="text-slate-500 text-xs border-b border-slate-700">
          <tr><th className="text-left p-3">ID</th><th>Name</th><th>Type</th><th>Insider link</th></tr>
        </thead>
        <tbody>
          {traders.map((t) => (
            <tr key={t.id} className="border-b border-slate-700/30 hover:bg-surface-light">
              <td className="p-3"><Link to={`/traders/${t.external_id}`} className="text-accent-cyan font-mono">{t.external_id}</Link></td>
              <td>{t.name}</td>
              <td className="text-slate-400">{t.account_type}</td>
              <td>{t.is_insider_linked ? <span className="text-red-400">Yes</span> : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
