import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import SeverityBadge from '../components/SeverityBadge'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import bash from 'react-syntax-highlighter/dist/esm/languages/hljs/bash'
import { githubGist } from 'react-syntax-highlighter/dist/esm/styles/hljs'

SyntaxHighlighter.registerLanguage('bash', bash)

const API = import.meta.env.VITE_API_URL

export default function ScanDetail() {
  const { scanId } = useParams()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['scan', scanId],
    queryFn: () => axios.get(`${API}/scans/${scanId}`).then(r => r.data)
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  )

  if (!data) return <div className="text-center py-12 text-gray-400">Scan not found</div>

  const failures = data.findings.filter(f => f.status === 'FAIL')
  const passes = data.findings.filter(f => f.status === 'PASS')

  return (
    <div>
      <button
        onClick={() => navigate('/scans')}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 mb-6 transition-colors"
      >
        <ArrowLeft size={16} /> Back to scans
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-semibold text-gray-900">{data.scan_name}</h1>
            <StatusBadge status={data.overall_status} />
          </div>
          <p className="text-gray-400 text-sm">{new Date(data.scanned_at).toLocaleString()} · Scan ID: {data.scan_id} · {data.resources_found} resources</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-semibold text-gray-900">{data.score}%</p>
          <p className="text-sm text-gray-400">{data.passed} passed / {data.failed} failed</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-6">
        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => (
          <div key={sev} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <SeverityBadge severity={sev} />
            <p className="text-2xl font-semibold text-gray-900 mt-2">{data.severity_breakdown[sev]}</p>
          </div>
        ))}
      </div>

      {failures.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-medium text-gray-900 mb-3">Failed rules ({failures.length})</h2>
          <div className="space-y-2">
            {failures.map((f, i) => (
              <div key={i} className="bg-white rounded-xl border border-red-100 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <XCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm font-medium text-gray-900">{f.rule_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={f.severity} />
                    <span className="font-mono text-xs text-gray-400">{f.rule_id}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 ml-6 mb-1">{f.message}</p>
                <p className="text-xs text-gray-400 ml-6">Resource: <span className="font-mono text-gray-600">{f.resource}</span></p>
                {f.remediation && (
                  <div className="ml-6 mt-2 bg-blue-50 rounded-lg px-3 py-2">
                    <p className="text-xs text-blue-700"><span className="font-medium">Fix:</span> {f.remediation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {passes.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-medium text-gray-900 mb-3">Passed rules ({passes.length})</h2>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {passes.map((f, i) => (
              <div key={i} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span className="text-sm text-gray-700">{f.rule_name}</span>
                </div>
                <span className="font-mono text-xs text-gray-400">{f.rule_id}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.tf_code && (
        <div>
          <h2 className="text-sm font-medium text-gray-900 mb-3">Scanned code</h2>
          <div className="rounded-xl overflow-hidden border border-gray-200">
            <SyntaxHighlighter
              language="bash"
              style={githubGist}
              customStyle={{ margin: 0, padding: '1rem', fontSize: '12px' }}
            >
              {data.tf_code}
            </SyntaxHighlighter>
          </div>
        </div>
      )}
    </div>
  )
}