from ..database.db import get_connection


def list_products():
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM products ORDER BY product_id")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_product(product_id: int):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
