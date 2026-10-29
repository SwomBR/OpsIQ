// Sample API responses and a fake fetch() for the component tests.
// The numbers are small and made up; they only need to be consistent.

import { vi } from 'vitest'

export const fixtures = {
  '/api/v1/analytics/dataset-info': {
    first_purchase_date: '2017-01-05 10:00:00',
    last_purchase_date: '2018-08-30 18:30:00',
    calculated_at: '2026-10-29T05:52:04Z',
  },
  '/api/v1/analytics/summary': {
    total_orders: 12000,
    delivered_orders: 11000,
    delivered_percentage: 91.67,
    late_delivered_orders: 900,
  },
  '/api/v1/analytics/orders-by-status': {
    total_orders: 12000,
    orders_by_status: { canceled: 300, delivered: 11000, shipped: 700 },
  },
  '/api/v1/analytics/delivery-performance': {
    delivered_orders_analyzed: 10995,
    on_time_orders: 10095,
    late_orders: 900,
    skipped_orders: 5,
    on_time_percentage: 91.81,
    late_percentage: 8.19,
    average_delay_days: 9.12,
    maximum_delay_days: 120.5,
    delayed_more_than_3_days: 600,
    delayed_more_than_7_days: 400,
  },
  '/api/v1/analytics/delivery-exceptions': {
    total_exceptions: 900,
    limit: 10,
    exceptions: [
      {
        order_id: 'order-severe',
        estimated_delivery: '2018-03-15 00:00:00',
        actual_delivery: '2018-07-13 12:00:00',
        days_late: 120.5,
      },
      {
        order_id: 'order-minor',
        estimated_delivery: '2018-03-15 00:00:00',
        actual_delivery: '2018-03-16 12:00:00',
        days_late: 1.5,
      },
    ],
  },
  '/api/v1/analytics/sales': {
    total_product_revenue: 1500000.5,
    total_freight_value: 250000.25,
    orders_with_items: 11800,
    average_product_value_per_order: 127.12,
    payment_totals_by_method: { boleto: 300000, credit_card: 1400000 },
  },
  '/api/v1/analytics/products': {
    total_products: 3200,
    products_missing_category: 61,
    top_categories: [
      { category: 'health_beauty', revenue: 125000, quantity_sold: 900 },
      { category: 'watches_gifts', revenue: 120000, quantity_sold: 600 },
    ],
    top_products: [{ product_id: 'product-1', quantity_sold: 52, revenue: 3760.9 }],
  },
  '/api/v1/analytics/customers': {
    total_unique_customers: 9600,
    repeat_customers: 300,
    repeat_customer_percentage: 3.13,
    customers_by_state: { SP: 4000, RJ: 1200, MG: 1100 },
  },
}

export function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

/**
 * Replace the global fetch with one that answers from `responses`
 * (default: the fixtures above). A response may be a function of the
 * URL, to vary the answer. Returns the mock, to inspect its calls.
 */
export function mockFetch(responses = fixtures) {
  const fetchMock = vi.fn(async (url) => {
    const { pathname } = new URL(url)
    const response = responses[pathname]

    if (response === undefined) return jsonResponse({ detail: 'Not Found' }, 404)
    if (typeof response === 'function') return response(url)
    return jsonResponse(response)
  })

  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}
