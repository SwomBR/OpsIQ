// Formatting helpers. Each returns an en dash when the value is missing,
// so a null from the API never shows up as "NaN" or "null".

const MISSING = '–'

const isMissing = (value) =>
  value === null || value === undefined || Number.isNaN(value)

const integerFormat = new Intl.NumberFormat('en-US')

const compactFormat = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

// The Olist dataset records money in Brazilian reais.
const currencyFormat = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const compactCurrencyFormat = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumFractionDigits: 2,
})

const dateFormat = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})

const dateTimeFormat = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

export function formatNumber(value) {
  return isMissing(value) ? MISSING : integerFormat.format(value)
}

export function formatCompactNumber(value) {
  return isMissing(value) ? MISSING : compactFormat.format(value)
}

export function formatPercent(value) {
  return isMissing(value) ? MISSING : `${value.toFixed(2)}%`
}

export function formatCurrency(value) {
  return isMissing(value) ? MISSING : currencyFormat.format(value)
}

export function formatCompactCurrency(value) {
  return isMissing(value) ? MISSING : compactCurrencyFormat.format(value)
}

export function formatDays(value) {
  if (isMissing(value)) return MISSING
  return `${value.toFixed(2)} ${value === 1 ? 'day' : 'days'}`
}

/**
 * Parse an API timestamp. Order dates arrive as "YYYY-MM-DD HH:MM:SS"
 * with no time zone; they are shown exactly as recorded, so they are
 * read as local time and never shifted.
 */
function parseTimestamp(value) {
  if (!value) return null
  const date = new Date(String(value).replace(' ', 'T'))
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(value) {
  const date = parseTimestamp(value)
  return date ? dateFormat.format(date) : MISSING
}

export function formatDateTime(value) {
  const date = parseTimestamp(value)
  return date ? dateTimeFormat.format(date) : MISSING
}

/** "credit_card" -> "Credit card", "health_beauty" -> "Health beauty". */
export function humanizeLabel(value) {
  if (!value) return MISSING
  const words = String(value).replaceAll('_', ' ').trim()
  return words.charAt(0).toUpperCase() + words.slice(1)
}
