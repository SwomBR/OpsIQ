import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import {
  formatCompactCurrency,
  formatCurrency,
  formatNumber,
} from '../../utils/format'
import { paymentMethodItems } from '../../utils/transform'
import { AsyncContent } from '../AsyncContent'
import { BarList } from '../BarList'
import { Section } from '../Section'
import { StatGrid, StatTile } from '../StatTile'

export function SalesSection() {
  const result = useApi(api.getSales)

  return (
    <Section
      id="sales"
      title="Sales and payments"
      description="Item prices and freight from the order items, in Brazilian reais (BRL)."
    >
      <AsyncContent result={result} lines={6}>
        {(data) => (
          <div className="stack">
            <StatGrid label="Sales metrics" pairs>
              <StatTile
                label="Product revenue"
                value={formatCompactCurrency(data.total_product_revenue)}
                note={formatCurrency(data.total_product_revenue)}
              />
              <StatTile
                label="Freight value"
                value={formatCompactCurrency(data.total_freight_value)}
                note={formatCurrency(data.total_freight_value)}
              />
              <StatTile
                label="Orders with items"
                value={formatNumber(data.orders_with_items)}
              />
              <StatTile
                label="Avg. product value per order"
                value={formatCurrency(data.average_product_value_per_order)}
                note="Freight not included"
              />
            </StatGrid>

            <div>
              <h3 className="subheading">Payments by method</h3>
              <BarList
                items={paymentMethodItems(data.payment_totals_by_method)}
                label="Payment totals by method"
                formatValue={formatCompactCurrency}
              />
            </div>

            <p className="footnote">
              Product revenue is the sum of item prices, not total company
              revenue. Payment totals include vouchers and instalments, so they
              do not equal product revenue plus freight.
            </p>
          </div>
        )}
      </AsyncContent>
    </Section>
  )
}
