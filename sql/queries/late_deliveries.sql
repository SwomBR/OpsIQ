-- Late-delivery analysis: the 10 most delayed delivered orders.
-- Only order fields are selected, never customer details.
SELECT
    order_id,
    order_estimated_delivery_date AS estimated_delivery,
    order_delivered_customer_date AS actual_delivery,
    ROUND(
        julianday(order_delivered_customer_date)
            - julianday(order_estimated_delivery_date),
        2
    ) AS days_late
FROM orders
WHERE order_status = 'delivered'
  AND julianday(order_delivered_customer_date)
        > julianday(order_estimated_delivery_date)
ORDER BY days_late DESC, order_id
LIMIT 10;
