-- Delivery performance: delivered orders compared with their estimated
-- delivery date. Uses the same rules as src/delivery_analyzer.py:
--   * only orders with status "delivered";
--   * orders missing either date are skipped;
--   * "late" means delivered after the estimated date and time.
-- julianday() turns a timestamp into a number of days, so subtracting
-- two of them gives the delay in days (with fractions).
WITH delivered AS (
    SELECT
        julianday(order_delivered_customer_date)
            - julianday(order_estimated_delivery_date) AS delay_days
    FROM orders
    WHERE order_status = 'delivered'
      AND julianday(order_delivered_customer_date) IS NOT NULL
      AND julianday(order_estimated_delivery_date) IS NOT NULL
)
SELECT
    COUNT(*)                                             AS delivered_orders_analyzed,
    SUM(delay_days <= 0)                                 AS on_time_orders,
    SUM(delay_days > 0)                                  AS late_orders,
    ROUND(100.0 * SUM(delay_days <= 0) / COUNT(*), 2)    AS on_time_percentage,
    ROUND(100.0 * SUM(delay_days > 0) / COUNT(*), 2)     AS late_percentage,
    ROUND(AVG(CASE WHEN delay_days > 0 THEN delay_days END), 2)
                                                         AS average_delay_days,
    ROUND(MAX(CASE WHEN delay_days > 0 THEN delay_days END), 2)
                                                         AS maximum_delay_days,
    SUM(delay_days > 3)                                  AS delayed_more_than_3_days,
    SUM(delay_days > 7)                                  AS delayed_more_than_7_days
FROM delivered;
