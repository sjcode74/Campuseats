-- Auth Service
CREATE TABLE users (
    user_id       VARCHAR(36) PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20) NOT NULL, -- 'student', 'restaurant_staff', 'runner', 'admin'
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catalog Service
CREATE TABLE restaurants (
    restaurant_id VARCHAR(36) PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    is_open       BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu_items (
    item_id       VARCHAR(36) PRIMARY KEY,
    restaurant_id VARCHAR(36) NOT NULL,
    name          VARCHAR(150) NOT NULL,
    price         DECIMAL(10,2) NOT NULL,
    is_available  BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- Order Service
CREATE TABLE orders (
    order_id      VARCHAR(36) PRIMARY KEY,
    user_id       VARCHAR(36) NOT NULL,
    restaurant_id VARCHAR(36) NOT NULL,
    status        VARCHAR(30) NOT NULL, -- 'pending_payment', 'placed', 'preparing', 'ready', 'completed', 'cancelled'
    total_amount  DECIMAL(10,2) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id VARCHAR(36) PRIMARY KEY,
    order_id      VARCHAR(36) NOT NULL,
    item_id       VARCHAR(36) NOT NULL, -- references Catalog's item, but no FK across services
    quantity      INT NOT NULL,
    price_at_order DECIMAL(10,2) NOT NULL, -- price snapshot at order time
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Payment Service
CREATE TABLE payments (
    payment_id    VARCHAR(36) PRIMARY KEY,
    order_id      VARCHAR(36) NOT NULL, -- reference by ID only, no cross-service FK
    amount        DECIMAL(10,2) NOT NULL,
    status        VARCHAR(20) NOT NULL, -- 'success', 'failed'
    payment_method VARCHAR(30) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery Service
CREATE TABLE deliveries (
    delivery_id   VARCHAR(36) PRIMARY KEY,
    order_id      VARCHAR(36) NOT NULL, -- reference by ID only
    runner_id     VARCHAR(36),          -- reference by ID only (points to a user)
    status        VARCHAR(20) NOT NULL, -- 'assigned', 'picked_up', 'delivered'
    assigned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification Service
CREATE TABLE notifications (
    notification_id VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) NOT NULL, -- reference by ID only
    message         TEXT NOT NULL,
    type            VARCHAR(30) NOT NULL, -- 'order_update', 'delivery_update'
    sent_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);