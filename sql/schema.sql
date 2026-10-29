-- OpsIQ SQLite schema.
--
-- One table per Olist CSV file that OpsIQ uses. Column names match the
-- CSV headers so every value can be traced back to its source file.
-- Timestamps are stored as TEXT in "YYYY-MM-DD HH:MM:SS" format, which
-- SQLite's date functions (such as julianday) understand. Empty CSV
-- values are stored as NULL.
--
-- Relationships:
--   customers 1 ── * orders           (orders.customer_id)
--   orders    1 ── * order_items      (order_items.order_id)
--   orders    1 ── * order_payments   (order_payments.order_id)
--   products  1 ── * order_items      (order_items.product_id)
--   sellers   1 ── * order_items      (order_items.seller_id)
--
-- products.product_category_name is NOT a foreign key to
-- category_translations: two categories in the data have no translation.

PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id              TEXT PRIMARY KEY,
    -- One person can have several customer_ids (one per order).
    customer_unique_id       TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city            TEXT,
    customer_state           TEXT
);

CREATE TABLE sellers (
    seller_id              TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city            TEXT,
    seller_state           TEXT
);

CREATE TABLE category_translations (
    product_category_name         TEXT PRIMARY KEY,
    product_category_name_english TEXT NOT NULL
);

CREATE TABLE products (
    product_id                 TEXT PRIMARY KEY,
    product_category_name      TEXT,
    -- "lenght" is spelled this way in the source CSV.
    product_name_lenght        INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty         INTEGER,
    product_weight_g           INTEGER,
    product_length_cm          INTEGER,
    product_height_cm          INTEGER,
    product_width_cm           INTEGER
);

CREATE TABLE orders (
    order_id                      TEXT PRIMARY KEY,
    customer_id                   TEXT NOT NULL REFERENCES customers (customer_id),
    order_status                  TEXT NOT NULL,
    order_purchase_timestamp      TEXT,
    order_approved_at             TEXT,
    order_delivered_carrier_date  TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT
);

CREATE TABLE order_items (
    order_id            TEXT    NOT NULL REFERENCES orders (order_id),
    -- Position of the item inside its order: 1, 2, 3, ...
    order_item_id       INTEGER NOT NULL,
    product_id          TEXT    NOT NULL REFERENCES products (product_id),
    seller_id           TEXT    NOT NULL REFERENCES sellers (seller_id),
    shipping_limit_date TEXT,
    price               REAL    NOT NULL CHECK (price >= 0),
    freight_value       REAL    NOT NULL CHECK (freight_value >= 0),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE order_payments (
    order_id             TEXT    NOT NULL REFERENCES orders (order_id),
    payment_sequential   INTEGER NOT NULL,
    payment_type         TEXT    NOT NULL,
    payment_installments INTEGER,
    payment_value        REAL    NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);

-- Indexes speed up the joins and filters used by the example queries.
CREATE INDEX idx_customers_unique_id ON customers (customer_unique_id);
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_status ON orders (order_status);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);
CREATE INDEX idx_order_items_seller_id ON order_items (seller_id);
CREATE INDEX idx_order_payments_type ON order_payments (payment_type);
