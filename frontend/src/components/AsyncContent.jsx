/** Placeholder blocks shown while data loads. */
export function LoadingState({ lines = 3 }) {
  return (
    <div className="loading" aria-busy="true">
      <span className="visually-hidden" role="status">
        Loading…
      </span>
      {Array.from({ length: lines }, (_, index) => (
        <span key={index} className="loading__line" aria-hidden="true" />
      ))}
    </div>
  )
}

/** A failed request, with its message and a button to try again. */
export function ErrorState({ error, onRetry }) {
  return (
    <div className="message message--error" role="alert">
      <p className="message__title">This section could not be loaded.</p>
      <p className="message__text">
        {error?.message || 'An unknown error occurred.'}
      </p>
      {onRetry && (
        <button type="button" className="button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

/** Shown when a request succeeded but there is nothing to display. */
export function EmptyState({ children }) {
  return (
    <div className="message">
      <p className="message__text">{children}</p>
    </div>
  )
}

/**
 * Show the right state for a useApi() result:
 * loading placeholder, error message, or children(data).
 */
export function AsyncContent({ result, lines, children }) {
  if (result.status === 'error') {
    return <ErrorState error={result.error} onRetry={result.retry} />
  }

  if (result.data === null) {
    return <LoadingState lines={lines} />
  }

  return children(result.data)
}
