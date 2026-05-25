import { severityBadge } from '../services/api'

export default function SeverityBadge({ severity }) {
  return <span className={severityBadge(severity)}>{severity}</span>
}
