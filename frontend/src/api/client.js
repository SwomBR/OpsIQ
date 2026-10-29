// Every request to the OpsIQ backend goes through this file, so the
// address of the API and the error handling live in one place.

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

// Vite only exposes environment variables that start with VITE_ to the
// browser. Set VITE_API_BASE_URL in frontend/.env.local (development) or
// in your hosting provider (production). Never put secrets here: every
// VITE_ value is visible to anyone who opens the website.
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    // The HTTP status code, or 0 when the API could not be reached.
    this.status = status
  }
}

/**
 * Request a path under /api/v1 and return the parsed JSON body.
 * Throws ApiError with a message that is safe to show to the user.
 */
export async function fetchJson(path, { signal } = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
      signal,
      headers: { Accept: 'application/json' },
    })
  } catch (error) {
    // The component stopped waiting (for example, it was removed).
    if (error.name === 'AbortError') throw error

    throw new ApiError(
      `Could not reach the OpsIQ API at ${API_BASE_URL}. ` +
        'Check that the backend is running.',
      0,
    )
  }

  if (!response.ok) {
    let detail = null

    try {
      const body = await response.json()
      // FastAPI sends {"detail": "..."} for the errors OpsIQ raises.
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // The error body was not JSON; use the generic message below.
    }

    throw new ApiError(
      detail || `The API returned an error (HTTP ${response.status}).`,
      response.status,
    )
  }

  return response.json()
}

// One function per endpoint. Each takes an AbortSignal so a request can
// be cancelled when the component that asked for it goes away.
export const api = {
  getDatasetInfo: (signal) => fetchJson('/analytics/dataset-info', { signal }),
  getSummary: (signal) => fetchJson('/analytics/summary', { signal }),
  getOrdersByStatus: (signal) =>
    fetchJson('/analytics/orders-by-status', { signal }),
  getDeliveryPerformance: (signal) =>
    fetchJson('/analytics/delivery-performance', { signal }),
  getDeliveryExceptions: (limit, signal) =>
    fetchJson(
      `/analytics/delivery-exceptions?${new URLSearchParams({ limit })}`,
      { signal },
    ),
  getSales: (signal) => fetchJson('/analytics/sales', { signal }),
  getProducts: (signal) => fetchJson('/analytics/products', { signal }),
  getCustomers: (signal) => fetchJson('/analytics/customers', { signal }),
}
