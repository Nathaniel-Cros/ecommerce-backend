"""SQLite schema bootstrap for tests without using SQLAlchemy create_all."""

from sqlalchemy import Engine


def reset_sqlite_schema(engine: Engine) -> None:
    """Drop and recreate required tables for integration tests."""

    with engine.begin() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=OFF;")

        connection.exec_driver_sql("DROP TABLE IF EXISTS payments;")
        connection.exec_driver_sql("DROP TABLE IF EXISTS order_items;")
        connection.exec_driver_sql("DROP TABLE IF EXISTS orders;")
        connection.exec_driver_sql("DROP TABLE IF EXISTS products;")

        connection.exec_driver_sql(
            """
            CREATE TABLE products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NULL,
                price_cents INTEGER NOT NULL,
                currency TEXT NOT NULL,
                stock INTEGER NOT NULL,
                is_active INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.exec_driver_sql(
            """
            CREATE TABLE orders (
                id TEXT PRIMARY KEY,
                order_number TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                status TEXT NOT NULL,
                total_cents INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.exec_driver_sql(
            """
            CREATE TABLE order_items (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                product_name_snapshot TEXT NOT NULL,
                unit_price_cents_snapshot INTEGER NOT NULL,
                line_total_cents INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
            );
            """
        )

        connection.exec_driver_sql(
            """
            CREATE TABLE payments (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                status TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                currency TEXT NOT NULL,
                external_payment_id TEXT NULL,
                init_point TEXT NULL,
                sandbox_init_point TEXT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
            );
            """
        )

        connection.exec_driver_sql("PRAGMA foreign_keys=ON;")
