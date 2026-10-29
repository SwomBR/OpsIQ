import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import { formatNumber, formatPercent } from '../../utils/format'
import { AsyncContent } from '../AsyncContent'
import { Section } from '../Section'
import { StatGrid, StatTile } from '../StatTile'

export function SummarySection() {
  const summary = useApi(api.getSummary)

  return (
    <Section id="summary" title="Order summary" className="span-full">
      <AsyncContent result={summary} lines={2}>
        {(data) => (
          <StatGrid label="Order summary">
            <StatTile
              label="Total orders"
              value={formatNumber(data.total_orders)}
              note="All order records"
            />
            <StatTile
              label="Delivered orders"
              value={formatNumber(data.delivered_orders)}
              note="Status is delivered"
            />
            <StatTile
              label="Delivered share"
              value={formatPercent(data.delivered_percentage)}
              note="Delivered ÷ total orders"
            />
            <StatTile
              label="Late deliveries"
              value={formatNumber(data.late_delivered_orders)}
              note="Arrived after the estimated date"
            />
          </StatGrid>
        )}
      </AsyncContent>
    </Section>
  )
}
