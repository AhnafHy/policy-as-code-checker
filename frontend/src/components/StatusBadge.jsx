export default function StatusBadge({ status }) {
  const styles = {
    PASS: 'bg-green-50 text-green-700 border-green-200',
    FAIL: 'bg-red-50 text-red-700 border-red-200',
    CRITICAL: 'bg-red-100 text-red-800 border-red-300',
    HIGH: 'bg-orange-50 text-orange-700 border-orange-200',
    MEDIUM: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    LOW: 'bg-blue-50 text-blue-700 border-blue-200',
  }
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${styles[status] || 'bg-gray-50 text-gray-700 border-gray-200'}`}>
      {status}
    </span>
  )
}