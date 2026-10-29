import { describe, expect, it } from 'vitest'

import {
  categoryItems,
  delayBandItems,
  delaySeverity,
  paymentMethodItems,
  topItemsWithOther,
  undeliveredStatusItems,
} from './transform'

describe('undeliveredStatusItems', () => {
  it('leaves out delivered orders and sorts largest first', () => {
    expect(
      undeliveredStatusItems({
        canceled: 625,
        delivered: 96478,
        shipped: 1107,
        approved: 2,
      }),
    ).toEqual([
      { key: 'shipped', label: 'Shipped', value: 1107 },
      { key: 'canceled', label: 'Canceled', value: 625 },
      { key: 'approved', label: 'Approved', value: 2 },
    ])
  })

  it('returns an empty list for missing data', () => {
    expect(undeliveredStatusItems()).toEqual([])
    expect(undeliveredStatusItems({ delivered: 5 })).toEqual([])
  })
})

describe('delayBandItems', () => {
  it('splits late orders into bands that add up to the total', () => {
    const bands = delayBandItems({
      late_orders: 7826,
      delayed_more_than_3_days: 5164,
      delayed_more_than_7_days: 3345,
    })

    expect(bands.map((band) => band.value)).toEqual([2662, 1819, 3345])
    expect(bands.reduce((sum, band) => sum + band.value, 0)).toBe(7826)
  })

  it('returns an empty list without data', () => {
    expect(delayBandItems(null)).toEqual([])
  })
})

describe('topItemsWithOther', () => {
  it('keeps the largest entries and adds the rest as "Other"', () => {
    expect(topItemsWithOther({ SP: 40, RJ: 12, MG: 11, AC: 2, AP: 1 }, 2, 'Other states')).toEqual([
      { key: 'SP', label: 'SP', value: 40 },
      { key: 'RJ', label: 'RJ', value: 12 },
      { key: '__other__', label: 'Other states (3)', value: 14 },
    ])
  })

  it('adds no "Other" item when everything fits', () => {
    expect(topItemsWithOther({ SP: 40 }, 10, 'Other')).toEqual([
      { key: 'SP', label: 'SP', value: 40 },
    ])
  })
})

describe('paymentMethodItems and categoryItems', () => {
  it('sorts payments largest first with readable labels', () => {
    expect(paymentMethodItems({ boleto: 10, credit_card: 50 })).toEqual([
      { key: 'credit_card', label: 'Credit card', value: 50 },
      { key: 'boleto', label: 'Boleto', value: 10 },
    ])
  })

  it('keeps the category order from the API', () => {
    expect(
      categoryItems([{ category: 'health_beauty', revenue: 5, quantity_sold: 2 }]),
    ).toEqual([{ key: 'health_beauty', label: 'Health beauty', value: 5, detail: 2 }])
  })
})

describe('delaySeverity', () => {
  it('uses the 3- and 7-day thresholds', () => {
    expect(delaySeverity(1).label).toBe('Minor')
    expect(delaySeverity(3).label).toBe('Minor')
    expect(delaySeverity(3.01).label).toBe('Major')
    expect(delaySeverity(7).label).toBe('Major')
    expect(delaySeverity(7.01).label).toBe('Severe')
  })
})
