-- E-commerce database schema (SQLite-compatible)
-- Users table
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  price REAL NOT NULL CHECK (price >= 0),
  stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
  image_url TEXT
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  order_date TEXT NOT NULL DEFAULT (datetime('now')),
  total_amount REAL NOT NULL CHECK (total_amount >= 0),
  status TEXT NOT NULL DEFAULT 'PENDING',
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  price_at_purchase REAL NOT NULL CHECK (price_at_purchase >= 0),
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Carts table (one active cart per user)
CREATE TABLE IF NOT EXISTS carts (
  cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Cart Items table
CREATE TABLE IF NOT EXISTS cart_items (
  cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  UNIQUE (cart_id, product_id),
  FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Seed data for products (10 items)
INSERT INTO products (name, description, price, stock_quantity, image_url) VALUES
('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 19.99, 150, 'https://picsum.photos/id/1/400/300'),
('Mechanical Keyboard', 'RGB backlit mechanical keyboard, blue switches', 69.99, 80, 'https://picsum.photos/id/2/400/300'),
('USB-C Charger', '65W fast charging USB-C wall charger', 29.99, 120, 'https://picsum.photos/id/3/400/300'),
('Noise Cancelling Headphones', 'Over-ear ANC Bluetooth headphones', 129.00, 60, 'https://picsum.photos/id/4/400/300'),
('4K Monitor', '27-inch 4K UHD IPS monitor', 329.00, 35, 'https://picsum.photos/id/5/400/300'),
('External SSD 1TB', 'Portable NVMe USB-C SSD', 99.50, 70, 'https://picsum.photos/id/6/400/300'),
('Webcam 1080p', 'Full HD webcam with microphone', 39.95, 90, 'https://picsum.photos/id/7/400/300'),
('Gaming Chair', 'Adjustable ergonomic gaming chair', 199.00, 25, 'https://picsum.photos/id/8/400/300'),
('Bluetooth Speaker', 'Portable waterproof Bluetooth speaker', 49.99, 110, 'https://picsum.photos/id/9/400/300'),
('Smartwatch', 'Fitness tracking smartwatch with GPS', 149.99, 55, 'https://picsum.photos/id/10/400/300');
