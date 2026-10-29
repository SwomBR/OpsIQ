-- Revenue by product category: the 10 categories with the most product
-- revenue (sum of item prices, freight excluded).
-- Category names follow src/product_analyzer.py: the English name when a
-- translation exists, otherwise the Portuguese name, otherwise "unknown".
SELECT
    COALESCE(
        t.product_category_name_english,
        NULLIF(p.product_category_name, ''),
        'unknown'
    ) AS category,
    ROUND(SUM(i.price), 2) AS revenue,
    COUNT(*)               AS items_sold
FROM order_items AS i
LEFT JOIN products AS p
    ON p.product_id = i.product_id
LEFT JOIN category_translations AS t
    ON t.product_category_name = p.product_category_name
GROUP BY category
ORDER BY revenue DESC
LIMIT 10;
