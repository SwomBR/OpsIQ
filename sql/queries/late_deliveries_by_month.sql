-- Late-delivery analysis by month: the share of delivered orders that
-- arrived late, grouped by the month the order was estimated to arrive.
SELECT
    substr(order_estimated_delivery_date, 1, 7) AS estimated_month,
    COUNT(*) AS delivered_orders,
    SUM(julianday(order_delivered_customer_date)
          > julianday(order_estimated_delivery_date)) AS late_orders,
    ROUND(
        100.0 * SUM(julianday(order_delivered_customer_date)
                      > julianday(order_estimated_delivery_date)) / COUNT(*),
        2
    ) AS late_percentage
FROM orders
WHERE order_status = 'delivered'
  AND julianday(order_delivered_customer_date) IS NOT NULL
  AND julianday(order_estimated_delivery_date) IS NOT NULL
GROUP BY estimated_month
ORDER BY estimated_month;
