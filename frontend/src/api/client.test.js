import { describe, expect, it, vi } from 'vitest'

import { jsonResponse, mockFetch } from '../test/mockApi'
import { API_BASE_URL, ApiError, api, fetchJson } from './client'

describe('API client', () => {
  it('reads the API address from VITE_API_BASE_URL', () => {
    expect(API_BASE_URL).toBe('http://api.test')
  })

  it('returns the JSON body of a successful response', async () => {
    const fetchMock = mockFetch({ '/api/v1/health': { status: 'healthy' } })

    await expect(fetchJson('/health')).resolves.toEqual({ status: 'healthy' })
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/health',
      expect.objectContaining({ headers: { Accept: 'application/json' } }),
    )
  })

  it('sends the exceptions limit as a query parameter', async () => {
    const fetchMock = mockFetch({
      '/api/v1/analytics/delivery-exceptions': { exceptions: [] },
    })

    await api.getDeliveryExceptions(25)

    expect(fetchMock.mock.calls[0][0]).toBe(
      'http://api.test/api/v1/analytics/delivery-exceptions?limit=25',
    )
  })

  it("uses the API's error message when there is one", async () => {
    mockFetch({
      '/api/v1/analytics/sales': () =>
        jsonResponse({ detail: 'The sales dataset is not available.' }, 503),
    })

    const error = await api.getSales().catch((caught) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(503)
    expect(error.message).toBe('The sales dataset is not available.')
  })

  it('uses a generic message when the error has no detail', async () => {
    mockFetch({
      '/api/v1/analytics/sales': () => new Response('oops', { status: 500 }),
    })

    await expect(api.getSales()).rejects.toThrow(
      'The API returned an error (HTTP 500).',
    )
  })

  it('explains when the API cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const error = await api.getSummary().catch((caught) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(0)
    expect(error.message).toContain('Could not reach the OpsIQ API at http://api.test')
  })

  it('passes cancellations through unchanged', async () => {
    const abort = new DOMException('Aborted', 'AbortError')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(abort))

    await expect(api.getSummary()).rejects.toBe(abort)
  })
})
