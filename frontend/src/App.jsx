import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Stocks from './pages/Stocks'
import StockDetail from './pages/StockDetail'
import Traders from './pages/Traders'
import TraderDetail from './pages/TraderDetail'
import GraphExplorer from './pages/GraphExplorer'
import SentimentSocial from './pages/SentimentSocial'
import Heatmaps from './pages/Heatmaps'
import DemoControl from './pages/DemoControl'

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="stocks" element={<Stocks />} />
        <Route path="stocks/:ticker" element={<StockDetail />} />
        <Route path="traders" element={<Traders />} />
        <Route path="traders/:id" element={<TraderDetail />} />
        <Route path="graph" element={<GraphExplorer />} />
        <Route path="sentiment" element={<SentimentSocial />} />
        <Route path="heatmaps" element={<Heatmaps />} />
        <Route path="demo" element={<DemoControl />} />
      </Route>
    </Routes>
  )
}
