/** One headline number with a label and an optional note below it. */
export function StatTile({ label, value, note }) {
  return (
    <div className="stat">
      <dt className="stat__label">{label}</dt>
      <dd className="stat__value">{value}</dd>
      {note && <dd className="stat__note">{note}</dd>}
    </div>
  )
}

/**
 * A responsive row of StatTiles, marked up as a description list.
 * `pairs` lays the tiles out two per row, so four tiles never wrap 3 + 1.
 */
export function StatGrid({ children, label, pairs = false }) {
  return (
    <dl className={pairs ? 'stat-grid stat-grid--pairs' : 'stat-grid'} aria-label={label}>
      {children}
    </dl>
  )
}
