 
-- ---------------------------------------------------------------------------
-- Enum types
-- ---------------------------------------------------------------------------
 
CREATE TYPE order_status AS ENUM (
    'Fila',
    'Pronto',
    'Entregue'
);
 
CREATE TYPE payment_method AS ENUM (
    'Cartão de Crédito',
    'Cartão de Debito',
    'Dinheiro',
    'Pix'
);
 
CREATE TYPE moviment_type AS ENUM (
    'Venda',
    'Entrada de Estoque',
    'Ajuste'
);
 
-- ---------------------------------------------------------------------------
-- products
-- ---------------------------------------------------------------------------
 
CREATE TABLE products (
    id            BIGSERIAL       PRIMARY KEY,
    name          VARCHAR         NOT NULL,
    category      VARCHAR         NOT NULL,
    price         NUMERIC(10, 2)  NOT NULL,
    priority      BOOLEAN         NOT NULL DEFAULT FALSE,
    image_data      BYTEA
);
 
-- ---------------------------------------------------------------------------
-- orders
-- ---------------------------------------------------------------------------
 
CREATE TABLE orders (
    id             BIGSERIAL                   PRIMARY KEY,
    created_at     TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    status         order_status                NOT NULL DEFAULT 'Fila',
    priority       BOOLEAN                     NOT NULL DEFAULT FALSE,
    payment_method payment_method              NOT NULL,
    total_price    NUMERIC(10, 2)              NOT NULL
);
 
-- Trigger to keep updated_at current on every UPDATE
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
 
-- ---------------------------------------------------------------------------
-- orders_items
-- ---------------------------------------------------------------------------
 
CREATE TABLE orders_items (
    id          BIGSERIAL       PRIMARY KEY,
    order_id    BIGINT          NOT NULL REFERENCES orders(id),
    product_id  BIGINT          NOT NULL REFERENCES products(id),
    quantity    INTEGER         NOT NULL,
    unit_price  NUMERIC(10, 2)  NOT NULL
);
 
-- ---------------------------------------------------------------------------
-- stock
-- ---------------------------------------------------------------------------
 
CREATE TABLE stock (
    product_id  BIGINT   PRIMARY KEY REFERENCES products(id),
    quantity    INTEGER  NOT NULL DEFAULT 0
);
 
-- ---------------------------------------------------------------------------
-- stock_moviments
-- ---------------------------------------------------------------------------
 
CREATE TABLE stock_moviments (
    id          BIGSERIAL       PRIMARY KEY,
    product_id  BIGINT          NOT NULL REFERENCES products(id),
    order_id    BIGINT                   REFERENCES orders(id),
    quantity    INTEGER         NOT NULL,
    type        moviment_type   NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
 
-- Trigger to update stock.quantity automatically on every stock_moviments INSERT.
-- quantity in stock_moviments is signed: positive = stock in, negative = stock out.
CREATE OR REPLACE FUNCTION update_stock_on_moviment()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE stock
    SET    quantity = quantity + NEW.quantity
    WHERE  product_id = NEW.product_id;
 
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trg_stock_moviments_update_stock
AFTER INSERT ON stock_moviments
FOR EACH ROW
EXECUTE FUNCTION update_stock_on_moviment();