// Turn API responses into the shapes the charts need. Kept separate from
// the components so the logic is easy to test on its own.

import { humanizeLabel } from './format'

/**
 * Orders in every status except "delivered", largest first.
 *
 * Delivered orders are ~97% of the data; on the same scale every other
 * status would be an invisible sliver, so they are charted separately
 * and the delivered total is shown in the summary instead.
 */
export function undeliveredStatusItems(ordersByStatus = {}) {
  return Object.entries(ordersByStatus)
    .filter(([status]) => status !== 'delivered')
    .map(([status, count]) => ({
      key: status,
      label: humanizeLabel(status),
      value: count,
    }))
    .sort((a, b) => b.value - a.value || a.key.localeCompare(b.key))
}

/**
 * Split late orders into three delay bands, using the same 3- and 7-day
 * thresholds as the backend's delivery-performance metrics.
 */
export function delayBandItems(performance) {
  if (!performance) return []

  const late = performance.late_orders ?? 0
  const over3 = performance.delayed_more_than_3_days ?? 0
  const over7 = performance.delayed_more_than_7_days ?? 0

  return [
    { key: 'up-to-3', label: 'Up to 3 days', value: late - over3 },
    { key: '3-to-7', label: 'Over 3, up to 7 days', value: over3 - over7 },
    { key: 'over-7', label: 'Over 7 days', value: over7 },
  ]
}

/**
 * Keep the `limit` largest entries of a {name: number} object and add
 * the rest together as one "Other" item, so long tails stay readable.
 */
export function topItemsWithOther(counts = {}, limit, otherLabel) {
  const sorted = Object.entries(counts).sort(
    ([nameA, a], [nameB, b]) => b - a || nameA.localeCompare(nameB),
  )

  const items = sorted.slice(0, limit).map(([name, value]) => ({
    key: name,
    label: name,
    value,
  }))

  const rest = sorted.slice(limit)

  if (rest.length > 0) {
    items.push({
      key: '__other__',
      label: `${otherLabel} (${rest.length})`,
      value: rest.reduce((total, [, value]) => total + value, 0),
    })
  }

  return items
}

/** Payment totals by method, largest first, with readable labels. */
export function paymentMethodItems(totals = {}) {
  return Object.entries(totals)
    .map(([method, value]) => ({
      key: method,
      label: humanizeLabel(method),
      value,
    }))
    .sort((a, b) => b.value - a.value)
}

/** Top categories by revenue, with readable labels. */
export function categoryItems(categories = []) {
  return categories.map((category) => ({
    key: category.category,
    label: humanizeLabel(category.category),
    value: category.revenue,
    detail: category.quantity_sold,
  }))
}

/**
 * How serious a delivery delay is. The 3- and 7-day thresholds match
 * the delivery-performance metrics.
 */
export function delaySeverity(daysLate) {
  if (daysLate > 7) return { level: 'critical', label: 'Severe' }
  if (daysLate > 3) return { level: 'serious', label: 'Major' }
  return { level: 'warning', label: 'Minor' }
}
