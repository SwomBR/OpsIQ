import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'
import { fixtures, jsonResponse, mockFetch } from './test/mockApi'

const section = (name) => screen.getByRole('region', { name })

describe('Dashboard', () => {
  it('shows every section with numbers from the API', async () => {
    mockFetch()
    render(<App />)

    expect(
      screen.getByRole('heading', { level: 1, name: 'Operations dashboard' }),
    ).toBeInTheDocument()

    const summary = section('Order summary')
    expect(await within(summary).findByText('12,000')).toBeInTheDocument()
    expect(within(summary).getByText('91.67%')).toBeInTheDocument()

    const delivery = section('Delivery performance')
    expect(await within(delivery).findByText('91.81%')).toBeInTheDocument()
    expect(within(delivery).getByText('9.12 days')).toBeInTheDocument()

    const status = section('Orders not delivered')
    const statusChart = await within(status).findByRole('list', {
      name: 'Orders by status, excluding delivered',
    })
    const statusRows = within(statusChart).getAllByRole('listitem')
    expect(statusRows.map((row) => row.querySelector('.bar-list__label').textContent)).toEqual([
      'Shipped',
      'Canceled',
    ])

    const exceptions = section('Delivery exceptions')
    expect(await within(exceptions).findByText('order-severe')).toBeInTheDocument()
    expect(within(exceptions).getByText('Showing 2 of 900 late-delivered orders.')).toBeInTheDocument()

    expect(await within(section('Sales and payments')).findByText('R$1.5M')).toBeInTheDocument()
    expect(
      await within(section('Products and categories')).findByRole('list', {
        name: 'Top categories by product revenue',
      }),
    ).toHaveTextContent('Health beauty')
    expect(await within(section('Customers')).findByText('9,600')).toBeInTheDocument()

    expect(await screen.findByText(/Orders placed 5 Jan 2017 – 30 Aug 2018/)).toBeInTheDocument()
  })

  it('makes one request per endpoint', async () => {
    const fetchMock = mockFetch()
    render(<App />)

    await screen.findByText('order-severe')
    await screen.findByText('9,600')

    const paths = fetchMock.mock.calls.map(([url]) => new URL(url).pathname)
    expect(paths.sort()).toEqual(Object.keys(fixtures).sort())
  })

  it('shows an error in one section without breaking the others', async () => {
    mockFetch({
      ...fixtures,
      '/api/v1/analytics/sales': () =>
        jsonResponse({ detail: 'The sales dataset is not available.' }, 503),
    })
    render(<App />)

    const sales = section('Sales and payments')
    expect(await within(sales).findByRole('alert')).toHaveTextContent(
      'The sales dataset is not available.',
    )
    expect(await within(section('Order summary')).findByText('12,000')).toBeInTheDocument()
  })

  it('loads the section again when "Try again" is pressed', async () => {
    let calls = 0
    mockFetch({
      ...fixtures,
      '/api/v1/analytics/summary': () => {
        calls += 1
        return calls === 1
          ? jsonResponse({ detail: 'Temporary problem.' }, 500)
          : jsonResponse(fixtures['/api/v1/analytics/summary'])
      },
    })
    render(<App />)

    const summary = section('Order summary')
    await userEvent.click(await within(summary).findByRole('button', { name: 'Try again' }))

    expect(await within(summary).findByText('12,000')).toBeInTheDocument()
  })

  it('requests more exceptions when the limit changes', async () => {
    const fetchMock = mockFetch()
    render(<App />)

    const exceptions = section('Delivery exceptions')
    await within(exceptions).findByText('order-severe')

    await userEvent.selectOptions(within(exceptions).getByLabelText('Show'), '50')

    await waitFor(() =>
      expect(fetchMock.mock.calls.map(([url]) => url)).toContain(
        'http://api.test/api/v1/analytics/delivery-exceptions?limit=50',
      ),
    )
  })

  it('shows empty states when there is no data', async () => {
    mockFetch({
      ...fixtures,
      '/api/v1/analytics/delivery-exceptions': {
        total_exceptions: 0,
        limit: 10,
        exceptions: [],
      },
      '/api/v1/analytics/delivery-performance': {
        ...fixtures['/api/v1/analytics/delivery-performance'],
        delivered_orders_analyzed: 0,
      },
    })
    render(<App />)

    expect(
      await within(section('Delivery exceptions')).findByText('No late deliveries were found.'),
    ).toBeInTheDocument()
    expect(
      await within(section('Delivery performance')).findByText(
        'No delivered orders with valid dates are available.',
      ),
    ).toBeInTheDocument()
  })
})
