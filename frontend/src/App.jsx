import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Shield, History, Plus, LayoutDashboard } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ScanHistory from './pages/ScanHistory'
import ScanDetail from './pages/ScanDetail'
import NewScan from './pages/NewScan'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="text-indigo-600" size={22} />
              <span className="font-semibold text-gray-900">Policy-as-Code Checker</span>
            </div>
            <div className="flex items-center gap-6">
              <NavLink to="/" className={({ isActive }) =>
                `flex items-center gap-1.5 text-sm font-medium ${isActive ? 'text-indigo-600' : 'text-gray-600 hover:text-gray-900'}`
              }>
                <LayoutDashboard size={15} /> Dashboard
              </NavLink>
              <NavLink to="/scans" className={({ isActive }) =>
                `flex items-center gap-1.5 text-sm font-medium ${isActive ? 'text-indigo-600' : 'text-gray-600 hover:text-gray-900'}`
              }>
                <History size={15} /> Scan History
              </NavLink>
              <NavLink to="/new" className={({ isActive }) =>
                `flex items-center gap-1.5 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors ${isActive ? 'opacity-90' : ''}`
              }>
                <Plus size={15} /> New Scan
              </NavLink>
            </div>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scans" element={<ScanHistory />} />
            <Route path="/scans/:scanId" element={<ScanDetail />} />
            <Route path="/new" element={<NewScan />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}