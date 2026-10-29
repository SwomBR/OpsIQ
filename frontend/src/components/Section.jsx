import { useId } from 'react'

/** A titled card that holds one part of the dashboard. */
export function Section({ id, title, description, actions, className = '', children }) {
  const headingId = useId()

  return (
    <section id={id} className={`card ${className}`} aria-labelledby={headingId}>
      <header className="card__header">
        <div>
          <h2 id={headingId} className="card__title">
            {title}
          </h2>
          {description && <p className="card__description">{description}</p>}
        </div>
        {actions && <div className="card__actions">{actions}</div>}
      </header>
      {children}
    </section>
  )
}
