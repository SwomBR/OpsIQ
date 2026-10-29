import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import { formatNumber } from '../../utils/format'
import { undeliveredStatusItems } from '../../utils/transform'
import { AsyncContent, EmptyState } from '../AsyncContent'
import { BarList } from '../BarList'
import { Section } from '../Section'

export function OrderStatusSection() {
  const result = useApi(api.getOrdersByStatus)

  return (
    <Section
      id="order-status"
      title="Orders not delivered"
      description="Orders in every status other than delivered."
    >
      <AsyncContent result={result} lines={6}>
        {(data) => {
          const items = undeliveredStatusItems(data.orders_by_status)
          const notDelivered = items.reduce((sum, item) => sum + item.value, 0)
          const delivered = data.orders_by_status.delivered ?? 0

          if (items.length === 0) {
            return <EmptyState>Every order has been delivered.</EmptyState>
          }

          return (
            <>
              <BarList items={items} label="Orders by status, excluding delivered" />
              <p className="footnote">
                {formatNumber(notDelivered)} orders in other statuses.{' '}
                {formatNumber(delivered)} delivered orders are left out so the
                smaller groups stay visible.
              </p>
            </>
          )
        }}
      </AsyncContent>
    </Section>
  )
}
