import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ChevronRight, Shield } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import SeverityBadge from '../components/SeverityBadge'

const API = import.meta.env.VITE_API_URL

export default function ScanHistory() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['scans'],
    queryFn: () => axios.get(`${API}/scans`).then(r => r.data)
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  )

  const scans = data || []

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Scan History</h1>
        <p className="text-gray-500 text-sm mt-1">{scans.length} scans total</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        {scans.length === 0 ? (
          <div className="p-12 text-center">
            <Shield className="mx-auto mb-3 text-gray-300" size={40} />
            <p className="text-gray-400">No scans yet — run your first scan</p>
          </div>
        ) : (
          scans.map(scan => (
            <div
              key={scan.scan_id}
              onClick={() => navigate(`/scans/${scan.scan_id}`)}
              className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <div className="flex items-center gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-gray-900">{scan.scan_name}</span>
                    <StatusBadge status={scan.overall_status} />
                  </div>
                  <p className="text-xs text-gray-400">{new Date(scan.scanned_at).toLocaleString()} · {scan.resources_found} resources</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  {scan.severity_critical > 0 && <SeverityBadge severity="CRITICAL" />}
                  {scan.severity_high > 0 && <SeverityBadge severity="HIGH" />}
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{scan.score}%</p>
                  <p className="text-xs text-gray-400">{scan.passed}P / {scan.failed}F</p>
                </div>
                <ChevronRight size={18} className="text-gray-400" />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}