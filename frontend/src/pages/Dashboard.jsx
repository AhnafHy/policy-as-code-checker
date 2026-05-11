import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ShieldCheck, ShieldAlert, BarChart3, AlertTriangle } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'

const API = import.meta.env.VITE_API_URL

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => axios.get(`${API}/dashboard`).then(r => r.data)
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  )

  if (error || !data || data.total_scans === 0) return (
    <div className="text-center py-20">
      <ShieldCheck className="mx-auto mb-4 text-gray-300" size={48} />
      <h2 className="text-xl font-semibold text-gray-700 mb-2">No scans yet</h2>
      <p className="text-gray-400 mb-6">Run your first Terraform security scan to see results here</p>
      <button
        onClick={() => navigate('/new')}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
      >
        Run first scan
      </button>
    </div>
  )

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Terraform policy compliance overview</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <BarChart3 size={18} />
            <span className="text-sm">Total scans</span>
          </div>
          <p className="text-3xl font-semibold text-gray-900">{data.total_scans}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <ShieldCheck size={18} />
            <span className="text-sm">Avg score</span>
          </div>
          <p className="text-3xl font-semibold text-gray-900">{data.avg_score}%</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-red-400 mb-2">
            <ShieldAlert size={18} />
            <span className="text-sm">Total failures</span>
          </div>
          <p className="text-3xl font-semibold text-gray-900">{data.total_failures}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-red-500 mb-2">
            <AlertTriangle size={18} />
            <span className="text-sm">Critical findings</span>
          </div>
          <p className="text-3xl font-semibold text-gray-900">{data.critical_findings}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="text-sm font-medium text-gray-900">Recent scans</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {data.recent_scans.map(scan => (
            <div
              key={scan.scan_id}
              onClick={() => navigate(`/scans/${scan.scan_id}`)}
              className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <div>
                <p className="text-sm font-medium text-gray-900">{scan.scan_name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{new Date(scan.scanned_at).toLocaleString()}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-600">{scan.score}%</span>
                <StatusBadge status={scan.overall_status} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}