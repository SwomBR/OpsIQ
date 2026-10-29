-- Repeat customers: people (customer_unique_id) with more than one order.
-- Each order has its own customer_id, so orders are joined to customers
-- to find the person behind every order.
WITH orders_per_person AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM orders AS o
    JOIN customers AS c
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*)                                          AS unique_customers,
    SUM(order_count > 1)                              AS repeat_customers,
    ROUND(100.0 * SUM(order_count > 1) / COUNT(*), 2) AS repeat_customer_percentage
FROM orders_per_person;
