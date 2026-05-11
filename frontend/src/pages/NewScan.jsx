import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Play, FileCode } from 'lucide-react'

const API = import.meta.env.VITE_API_URL

const EXAMPLE_TF = `# Example: Insecure Terraform config for testing
resource "aws_s3_bucket" "bad_bucket" {
  bucket        = "my-insecure-bucket"
  acl           = "public-read"
  force_destroy = true
}

resource "aws_db_instance" "bad_db" {
  identifier         = "my-db"
  engine             = "postgres"
  instance_class     = "db.t3.micro"
  allocated_storage  = 20
  username           = "admin"
  password           = "password123"
  storage_encrypted  = false
  publicly_accessible = true
  deletion_protection = false
  multi_az           = false
}

resource "aws_security_group" "bad_sg" {
  name = "wide-open-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}`

export default function NewScan() {
  const navigate = useNavigate()
  const [scanName, setScanName] = useState('')
  const [tfCode, setTfCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!tfCode.trim()) {
      setError('Please paste some Terraform code to scan')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await axios.post(`${API}/scan`, {
        scan_name: scanName || 'Unnamed Scan',
        terraform_code: tfCode
      })
      navigate(`/scans/${res.data.scan_id}`)
    } catch (err) {
      setError('Scan failed — please try again')
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">New Scan</h1>
        <p className="text-gray-500 text-sm mt-1">Paste your Terraform code to check for security misconfigurations</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Scan name</label>
        <input
          type="text"
          value={scanName}
          onChange={e => setScanName(e.target.value)}
          placeholder="e.g. Production infrastructure review"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-4"
        />

        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">Terraform code</label>
          <button
            onClick={() => setTfCode(EXAMPLE_TF)}
            className="flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            <FileCode size={12} />
            Load example (insecure config)
          </button>
        </div>
        <textarea
          value={tfCode}
          onChange={e => setTfCode(e.target.value)}
          placeholder="Paste your Terraform HCL code here..."
          rows={18}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors text-sm font-medium"
      >
        <Play size={15} />
        {loading ? 'Scanning...' : 'Run Security Scan'}
      </button>
    </div>
  )
}