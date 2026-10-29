import { formatNumber } from '../utils/format'

/**
 * A horizontal bar chart built from plain HTML.
 *
 * Every value is printed at the end of its bar, so nothing depends on
 * colour or on hovering. Hovering or focusing a row also shows its
 * share of the total. Bars share one scale, starting at zero.
 *
 * Props:
 *   items       [{ key, label, value, detail? }]
 *   label       accessible name for the whole chart
 *   formatValue turns a value into text (default: 1,234)
 *   formatDetail optional extra text for the tooltip, from item.detail
 *   colors      optional CSS colour per item (default: series colour 1)
 */
export function BarList({
  items,
  label,
  formatValue = formatNumber,
  formatDetail,
  colors,
}) {
  const largest = Math.max(0, ...items.map((item) => item.value))
  const total = items.reduce((sum, item) => sum + item.value, 0)

  return (
    <ul className="bar-list" aria-label={label}>
      {items.map((item, index) => {
        const width = largest > 0 ? (item.value / largest) * 100 : 0
        const share = total > 0 ? (item.value / total) * 100 : 0

        return (
          <li key={item.key} className="bar-list__row" tabIndex={0}>
            <span className="bar-list__label">{item.label}</span>
            <span className="bar-list__track" aria-hidden="true">
              <span
                className="bar-list__bar"
                style={{
                  width: `${width}%`,
                  ...(colors && { background: colors[index] }),
                }}
              />
            </span>
            <span className="bar-list__value">{formatValue(item.value)}</span>
            {/* The row already reads "label value", so screen readers
                skip this visual-only tooltip. */}
            <span className="tooltip" aria-hidden="true">
              <strong>{item.label}</strong>
              <span>{formatValue(item.value)}</span>
              <span>{share.toFixed(1)}% of total shown</span>
              {formatDetail && <span>{formatDetail(item.detail)}</span>}
            </span>
          </li>
        )
      })}
    </ul>
  )
}
