-- Orders by status: how many orders are in each status.
-- Matches GET /api/v1/analytics/orders-by-status.
SELECT
    order_status,
    COUNT(*) AS orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC;
