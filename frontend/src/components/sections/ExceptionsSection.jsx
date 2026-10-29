import { useCallback, useId, useState } from 'react'

import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import { formatDateTime, formatNumber } from '../../utils/format'
import { delaySeverity } from '../../utils/transform'
import { AsyncContent, EmptyState } from '../AsyncContent'
import { Section } from '../Section'

// The API accepts 1 to 100.
const LIMIT_OPTIONS = [10, 25, 50, 100]

const SEVERITY_ICONS = { critical: '▲', serious: '◆', warning: '●' }

export function SeverityBadge({ daysLate }) {
  const severity = delaySeverity(daysLate)

  return (
    <span className={`badge badge--${severity.level}`}>
      <span aria-hidden="true">{SEVERITY_ICONS[severity.level]}</span>
      {severity.label}
    </span>
  )
}

export function ExceptionsTable({ exceptions }) {
  if (exceptions.length === 0) {
    return <EmptyState>No late deliveries were found.</EmptyState>
  }

  return (
    <div className="table-scroll" tabIndex={0} aria-label="Delivery exceptions table">
      <table className="table">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">Order ID</th>
            <th scope="col">Estimated delivery</th>
            <th scope="col">Actual delivery</th>
            <th scope="col" className="numeric">
              Days late
            </th>
            <th scope="col">Severity</th>
          </tr>
        </thead>
        <tbody>
          {exceptions.map((exception, index) => (
            <tr key={exception.order_id}>
              <td className="muted numeric">{index + 1}</td>
              <td>
                <code className="id">{exception.order_id}</code>
              </td>
              <td>{formatDateTime(exception.estimated_delivery)}</td>
              <td>{formatDateTime(exception.actual_delivery)}</td>
              <td className="numeric strong">{exception.days_late.toFixed(2)}</td>
              <td>
                <SeverityBadge daysLate={exception.days_late} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ExceptionsSection() {
  const [limit, setLimit] = useState(LIMIT_OPTIONS[0])
  const selectId = useId()

  // A new function only when the limit changes, which starts a new request.
  const load = useCallback(
    (signal) => api.getDeliveryExceptions(limit, signal),
    [limit],
  )
  const result = useApi(load)

  const limitControl = (
    <label className="select" htmlFor={selectId}>
      <span>Show</span>
      <select
        id={selectId}
        value={limit}
        onChange={(event) => setLimit(Number(event.target.value))}
      >
        {LIMIT_OPTIONS.map((option) => (
          <option key={option} value={option}>
            {option} orders
          </option>
        ))}
      </select>
    </label>
  )

  return (
    <Section
      id="exceptions"
      title="Delivery exceptions"
      description="Late-delivered orders, longest delay first. Severity: over 7 days is severe, over 3 days is major."
      actions={limitControl}
      className="span-full"
    >
      <AsyncContent result={result} lines={8}>
        {(data) => (
          <div aria-busy={result.status === 'loading'} className="stack">
            <p className="footnote footnote--top">
              Showing {formatNumber(data.exceptions.length)} of{' '}
              {formatNumber(data.total_exceptions)} late-delivered orders.
            </p>
            <ExceptionsTable exceptions={data.exceptions} />
          </div>
        )}
      </AsyncContent>
    </Section>
  )
}
