import { NavLink, Outlet } from 'react-router-dom'
import { Shield, LayoutDashboard, Bell, LineChart, Users, GitBranch, MessageSquare, Grid3x3, Settings } from 'lucide-react'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/stocks', icon: LineChart, label: 'Stocks' },
  { to: '/traders', icon: Users, label: 'Traders' },
  { to: '/graph', icon: GitBranch, label: 'Insider Graph' },
  { to: '/sentiment', icon: MessageSquare, label: 'Sentiment & Social' },
  { to: '/heatmaps', icon: Grid3x3, label: 'Heatmaps' },
  { to: '/demo', icon: Settings, label: 'Demo Control' },
]

export default function MainLayout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-surface-light border-r border-slate-700/50 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-700/50">
          <div className="flex items-center gap-2">
            <Shield className="w-8 h-8 text-accent-cyan" />
            <div>
              <h1 className="font-bold text-white text-sm">MarketShield AI</h1>
              <p className="text-[10px] text-slate-500 font-mono">SURVEILLANCE DESK</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-2 space-y-0.5">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-accent/20 text-accent-cyan' : 'text-slate-400 hover:bg-surface-card hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <p className="p-3 text-[10px] text-slate-600 leading-tight">
          Synthetic demo data. Signals are not legal conclusions.
        </p>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
