import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import { formatDays, formatNumber } from '../../utils/format'
import { delayBandItems } from '../../utils/transform'
import { AsyncContent, EmptyState } from '../AsyncContent'
import { BarList } from '../BarList'
import { ProportionBar } from '../ProportionBar'
import { Section } from '../Section'
import { StatGrid, StatTile } from '../StatTile'

// Light to dark: a longer delay is a darker bar.
const DELAY_BAND_COLORS = [
  'var(--ordinal-1)',
  'var(--ordinal-2)',
  'var(--ordinal-3)',
]

export function DeliverySection() {
  const result = useApi(api.getDeliveryPerformance)

  return (
    <Section
      id="delivery"
      title="Delivery performance"
      description="Delivered orders compared with their estimated delivery date."
      className="span-wide"
    >
      <AsyncContent result={result} lines={6}>
        {(data) => {
          if (data.delivered_orders_analyzed === 0) {
            return (
              <EmptyState>
                No delivered orders with valid dates are available.
              </EmptyState>
            )
          }

          return (
            <div className="stack">
              <ProportionBar
                label={
                  `${data.on_time_percentage}% on time, ` +
                  `${data.late_percentage}% late`
                }
                segments={[
                  {
                    key: 'on-time',
                    label: 'On time',
                    value: data.on_time_orders,
                    percentage: data.on_time_percentage,
                    color: 'var(--series-1)',
                  },
                  {
                    key: 'late',
                    label: 'Late',
                    value: data.late_orders,
                    percentage: data.late_percentage,
                    color: 'var(--series-2)',
                  },
                ]}
              />

              <StatGrid label="Delay metrics">
                <StatTile
                  label="Average delay"
                  value={formatDays(data.average_delay_days)}
                  note="Among late orders"
                />
                <StatTile
                  label="Longest delay"
                  value={formatDays(data.maximum_delay_days)}
                />
                <StatTile
                  label="Over 3 days late"
                  value={formatNumber(data.delayed_more_than_3_days)}
                />
                <StatTile
                  label="Over 7 days late"
                  value={formatNumber(data.delayed_more_than_7_days)}
                />
              </StatGrid>

              <div>
                <h3 className="subheading">How late were late orders?</h3>
                <BarList
                  items={delayBandItems(data)}
                  label="Late orders by length of delay"
                  colors={DELAY_BAND_COLORS}
                />
              </div>

              <p className="footnote">
                Based on {formatNumber(data.delivered_orders_analyzed)} delivered
                orders. {formatNumber(data.skipped_orders)} delivered orders
                were skipped because a date was missing or unreadable.
              </p>
            </div>
          )
        }}
      </AsyncContent>
    </Section>
  )
}
