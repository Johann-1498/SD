-- PostgreSQL DDL for practica17 ESB demo.
-- Usage:
--   psql -U postgres -f init_db.sql
-- Or docker:
--   docker run --name pg-esb -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16

CREATE TABLE IF NOT EXISTS products (
    sku   VARCHAR(32) PRIMARY KEY,
    name  VARCHAR(128) NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS stock (
    id       SERIAL PRIMARY KEY,
    sku      VARCHAR(32) REFERENCES products(sku),
    warehouse VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);
