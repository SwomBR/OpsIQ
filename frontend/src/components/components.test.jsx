import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { AsyncContent } from './AsyncContent'
import { BarList } from './BarList'
import { ExceptionsTable } from './sections/ExceptionsSection'
import { StatGrid, StatTile } from './StatTile'

describe('StatTile', () => {
  it('shows the label, value, and note', () => {
    render(
      <StatGrid label="Example">
        <StatTile label="Total orders" value="99,441" note="All order records" />
      </StatGrid>,
    )

    expect(screen.getByText('Total orders')).toBeInTheDocument()
    expect(screen.getByText('99,441')).toBeInTheDocument()
    expect(screen.getByText('All order records')).toBeInTheDocument()
  })
})

describe('BarList', () => {
  const items = [
    { key: 'a', label: 'Shipped', value: 100 },
    { key: 'b', label: 'Canceled', value: 50 },
  ]

  it('prints every value as text', () => {
    render(<BarList items={items} label="Statuses" />)

    const rows = within(screen.getByRole('list', { name: 'Statuses' })).getAllByRole(
      'listitem',
    )
    expect(rows).toHaveLength(2)
    expect(rows[0]).toHaveTextContent('Shipped')
    expect(rows[0]).toHaveTextContent('100')
    expect(rows[1]).toHaveTextContent('Canceled')
  })

  it('sizes bars relative to the largest value', () => {
    const { container } = render(<BarList items={items} label="Statuses" />)

    const bars = container.querySelectorAll('.bar-list__bar')
    expect(bars[0].style.width).toBe('100%')
    expect(bars[1].style.width).toBe('50%')
  })

  it('handles all-zero values without dividing by zero', () => {
    const { container } = render(
      <BarList items={[{ key: 'a', label: 'None', value: 0 }]} label="Zero" />,
    )

    expect(container.querySelector('.bar-list__bar').style.width).toBe('0%')
  })
})

describe('AsyncContent', () => {
  const renderData = (data) => <p>Value: {data.value}</p>

  it('shows a loading state while there is no data', () => {
    render(
      <AsyncContent result={{ status: 'loading', data: null }}>{renderData}</AsyncContent>,
    )

    expect(screen.getByRole('status')).toHaveTextContent('Loading')
  })

  it('shows the data once it arrives', () => {
    render(
      <AsyncContent result={{ status: 'success', data: { value: 7 } }}>
        {renderData}
      </AsyncContent>,
    )

    expect(screen.getByText('Value: 7')).toBeInTheDocument()
  })

  it('shows the error message and a working retry button', async () => {
    const retry = vi.fn()

    render(
      <AsyncContent
        result={{ status: 'error', data: null, error: new Error('API down'), retry }}
      >
        {renderData}
      </AsyncContent>,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('API down')
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(retry).toHaveBeenCalledOnce()
  })
})

describe('ExceptionsTable', () => {
  it('shows one row per exception with dates, days late, and severity', () => {
    render(
      <ExceptionsTable
        exceptions={[
          {
            order_id: 'order-1',
            estimated_delivery: '2018-03-15 00:00:00',
            actual_delivery: '2018-09-19 23:24:07',
            days_late: 188.98,
          },
          {
            order_id: 'order-2',
            estimated_delivery: '2018-03-15 00:00:00',
            actual_delivery: '2018-03-19 00:00:00',
            days_late: 4,
          },
        ]}
      />,
    )

    const rows = screen.getAllByRole('row').slice(1)
    expect(rows).toHaveLength(2)
    expect(rows[0]).toHaveTextContent('order-1')
    expect(rows[0]).toHaveTextContent('15 Mar 2018, 00:00')
    expect(rows[0]).toHaveTextContent('19 Sept 2018, 23:24')
    expect(rows[0]).toHaveTextContent('188.98')
    expect(rows[0]).toHaveTextContent('Severe')
    expect(rows[1]).toHaveTextContent('Major')
  })

  it('shows an empty state when there are no exceptions', () => {
    render(<ExceptionsTable exceptions={[]} />)

    expect(screen.getByText('No late deliveries were found.')).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })
})
