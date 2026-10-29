-- Order and customer relationship: how many people placed 1, 2, 3, ...
-- orders. Shows only counts, never individual customers.
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
    order_count,
    COUNT(*) AS customers
FROM orders_per_person
GROUP BY order_count
ORDER BY order_count;
