import { formatNumber, formatPercent } from '../utils/format'

/**
 * One bar split into parts of a whole (for example on-time vs late),
 * with a legend that repeats every value as text.
 *
 * segments: [{ key, label, value, percentage, color }]
 */
export function ProportionBar({ segments, label }) {
  return (
    <figure className="proportion">
      <div className="proportion__bar" role="img" aria-label={label}>
        {segments.map((segment) => (
          <span
            key={segment.key}
            className="proportion__segment"
            style={{
              flexGrow: segment.value,
              background: segment.color,
            }}
          />
        ))}
      </div>
      <figcaption>
        <ul className="legend">
          {segments.map((segment) => (
            <li key={segment.key} className="legend__item">
              <span
                className="legend__swatch"
                style={{ background: segment.color }}
                aria-hidden="true"
              />
              <span className="legend__label">{segment.label}</span>
              <span className="legend__value">
                {formatPercent(segment.percentage)}
              </span>
              <span className="legend__detail">
                {formatNumber(segment.value)} orders
              </span>
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  )
}
