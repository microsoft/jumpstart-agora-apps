CREATE SCHEMA IF NOT EXISTS contoso;
CREATE TABLE IF NOT EXISTS contoso.products (productId SERIAL PRIMARY KEY, name text, description text, price numeric, stock int, photopath text, category text);
CREATE TABLE IF NOT EXISTS contoso.Orders (orderID SERIAL PRIMARY KEY, orderDate timestamp, orderdetails JSON, storeId INT);
CREATE TABLE IF NOT EXISTS contoso.checkout_type ( id SERIAL PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contoso.checkout_history ( timestamp TIMESTAMPTZ, checkout_id INT, checkout_type INT, queue_length INT, average_wait_time_seconds INT, PRIMARY KEY (timestamp, checkout_id));
CREATE TABLE IF NOT EXISTS contoso.checkout ( id INTEGER PRIMARY KEY, type INTEGER REFERENCES contoso.checkout_type(id), avgprocessingtime INTEGER, closed BOOLEAN);

INSERT INTO contoso.checkout (id, type, avgprocessingtime, closed)
SELECT *
FROM (VALUES
    (1, 'Standard', 60, false),
    (2, 'Standard', 60, false),
    (3, 'Express', 30, false),
    (4, 'Express', 30, false),
    (5, 'SelfService', 45, false),
    (6, 'SelfService', 45, false),
    (7, 'SelfService', 45, true),
    (8, 'SelfService', 45, true)
) AS data
WHERE NOT EXISTS (SELECT 1 FROM contoso.checkout);

INSERT INTO contoso.products (name, description, price, stock, photopath, category)
SELECT *
FROM (VALUES
    ('Red Apple', 'Contoso Fresh Fuji Red Apples', 0.5, 10000, 'static/img/product1.jpg', 'Fruits'),
    ('Banana', 'Contoso Fresh Cavendish Bananas', 1, 10000, 'static/img/product2.jpg', 'Fruits'),
    ('Avocado', 'Contoso Fresh Hass Avocado', 1.5, 10000, 'static/img/product3.jpg', 'Vegetables'),
    ('Bread', 'Instore Bakery Fresh Bread Rolls 6 pack', .80, 10000, 'static/img/product4.jpg', 'Bread'),
    ('Milk', 'Contoso Full Milk', 0.95, 10000, 'static/img/product5.jpg', 'Dairy'),
    ('Orange Juice', 'Contoso Premium Juice', 4, 10000, 'static/img/product6.jpg', 'Beverages'),
    ('Chips', 'Contoso Crinkle Cut Chips', 2.0, 10000, 'static/img/product7.jpg', 'Snacks'),
    ('Red Pepper', 'Contoso Fresh Red Pepper', 3.5, 10000, 'static/img/product8.jpg', 'Vegetables'),
    ('Lettuce', 'Fresh Vegetable Cos Lettuce', 7, 10000, 'static/img/product9.jpg', 'Vegetables'),
    ('Tomato', 'Contoso Fresh Vine Tomatoes', 1, 10000, 'static/img/product10.jpg', 'Vegetables'),
    ('Strawberry', 'Contoso Fresh Allstar Strawberries', 1, 10000, 'static/img/product11.jpg', 'Fruit'),
    ('Eggs', 'Free Range Contoso Dozen Eggs', 1, 10000, 'static/img/product12.jpg', 'Eggs'),
    ('Lemon', 'Contoso Lisbon Lemons', 1, 10000, 'static/img/product13.jpg', 'Fruit')
) AS data
WHERE NOT EXISTS (SELECT 1 FROM contoso.products);