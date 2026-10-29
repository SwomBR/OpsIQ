import { api } from '../api/client'
import { useApi } from '../hooks/useApi'
import { formatDate, formatDateTime } from '../utils/format'

const SECTION_LINKS = [
  ['#summary', 'Summary'],
  ['#delivery', 'Delivery'],
  ['#exceptions', 'Exceptions'],
  ['#sales', 'Sales'],
  ['#products', 'Products'],
  ['#customers', 'Customers'],
]

/** Describes the data period, using only what the API reports. */
function DataPeriod() {
  const info = useApi(api.getDatasetInfo)

  if (info.status !== 'success') return null

  const { first_purchase_date: first, last_purchase_date: last } = info.data

  return (
    <p className="app-header__meta">
      {first && last && (
        <span>
          Orders placed {formatDate(first)} – {formatDate(last)}
        </span>
      )}
      <span>
        Analytics calculated {formatDateTime(info.data.calculated_at)}
      </span>
    </p>
  )
}

export function Header() {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        <div className="brand">
          <span className="brand__mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <rect x="3" y="12" width="4" height="9" rx="1.5" />
              <rect x="10" y="7" width="4" height="14" rx="1.5" />
              <rect x="17" y="3" width="4" height="18" rx="1.5" />
            </svg>
          </span>
          <span className="brand__name">OpsIQ</span>
        </div>
        <h1 className="app-header__title">Operations dashboard</h1>
        <p className="app-header__description">
          Order, delivery, sales, product, and customer analytics from the
          Olist Brazilian e-commerce dataset.
        </p>
        <DataPeriod />
        <nav aria-label="Dashboard sections" className="section-nav">
          {SECTION_LINKS.map(([href, label]) => (
            <a key={href} href={href}>
              {label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  )
}
