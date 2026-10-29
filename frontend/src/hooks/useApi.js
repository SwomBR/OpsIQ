import { useCallback, useEffect, useState } from 'react'

/**
 * Load data with `load(signal)` and track its progress.
 *
 * Returns { status, data, error, retry }, where status is
 * 'loading', 'success', or 'error'.
 *
 * `load` must keep the same identity between renders (a module-level
 * function or one wrapped in useCallback); a new `load` starts a new
 * request. While a new request runs, the previous data stays available,
 * so tables do not jump around when an option changes.
 */
export function useApi(load) {
  const [attempt, setAttempt] = useState(0)
  // The latest finished request: which `load` and attempt it was for,
  // and what it returned.
  const [result, setResult] = useState({
    load: null,
    attempt: -1,
    data: null,
    error: null,
  })

  useEffect(() => {
    const controller = new AbortController()

    load(controller.signal)
      .then((data) => setResult({ load, attempt, data, error: null }))
      .catch((error) => {
        // Ignore requests we cancelled ourselves.
        if (controller.signal.aborted) return
        setResult({ load, attempt, data: null, error })
      })

    // Cancel the request if the component is removed or `load` changes.
    return () => controller.abort()
  }, [load, attempt])

  const retry = useCallback(() => setAttempt((count) => count + 1), [])

  // Still loading until the stored result belongs to the current request.
  const isCurrent = result.load === load && result.attempt === attempt
  let status = 'loading'
  if (isCurrent) status = result.error ? 'error' : 'success'

  return {
    status,
    data: result.data,
    error: isCurrent ? result.error : null,
    retry,
  }
}
