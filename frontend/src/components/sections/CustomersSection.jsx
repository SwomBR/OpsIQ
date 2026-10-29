import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import { formatNumber, formatPercent } from '../../utils/format'
import { topItemsWithOther } from '../../utils/transform'
import { AsyncContent, EmptyState } from '../AsyncContent'
import { BarList } from '../BarList'
import { Section } from '../Section'
import { StatGrid, StatTile } from '../StatTile'

const STATES_SHOWN = 10

export function CustomersSection() {
  const result = useApi(api.getCustomers)

  return (
    <Section
      id="customers"
      title="Customers"
      description="Unique people, identified by customer_unique_id. Only totals are shown, never individual customers."
      className="span-full"
    >
      <AsyncContent result={result} lines={6}>
        {(data) => (
          <div className="split">
            <StatGrid label="Customer metrics">
              <StatTile
                label="Unique customers"
                value={formatNumber(data.total_unique_customers)}
              />
              <StatTile
                label="Repeat customers"
                value={formatNumber(data.repeat_customers)}
                note="More than one order"
              />
              <StatTile
                label="Repeat customer rate"
                value={formatPercent(data.repeat_customer_percentage)}
              />
            </StatGrid>

            <div>
              <h3 className="subheading">Unique customers by state</h3>
              {Object.keys(data.customers_by_state).length === 0 ? (
                <EmptyState>No customer locations are available.</EmptyState>
              ) : (
                <BarList
                  items={topItemsWithOther(
                    data.customers_by_state,
                    STATES_SHOWN,
                    'Other states',
                  )}
                  label="Unique customers by state"
                />
              )}
              <p className="footnote">
                A few customers ordered from more than one state, so state
                counts add up to slightly more than the unique total.
              </p>
            </div>
          </div>
        )}
      </AsyncContent>
    </Section>
  )
}
