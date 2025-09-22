from ..database.db import get_connection


def place_order(user_id: int):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (user_id,))
        cart_row = cur.fetchone()
        if not cart_row:
            return None, "Cart not found"
        cart_id = cart_row["cart_id"]

        # Begin transaction
        conn.isolation_level = None  # Manual transaction control
        conn.execute("BEGIN IMMEDIATE")
        try:
            # Fetch cart items with product info
            cur = conn.execute(
                """
                SELECT ci.product_id, ci.quantity, p.price, p.stock_quantity
                FROM cart_items ci
                JOIN products p ON p.product_id = ci.product_id
                WHERE ci.cart_id = ?
                """,
                (cart_id,),
            )
            items = cur.fetchall()
            if not items:
                conn.execute("ROLLBACK")
                return None, "Cart is empty"

            # Check stock
            for r in items:
                if r["quantity"] > r["stock_quantity"]:
                    conn.execute("ROLLBACK")
                    return None, f"Insufficient stock for product {r['product_id']}"

            total_amount = sum(r["quantity"] * r["price"] for r in items)

            # Create order
            cur = conn.execute(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
                (user_id, total_amount, "PENDING"),
            )
            order_id = cur.lastrowid

            # Create order items and decrement stock
            for r in items:
                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                    (order_id, r["product_id"], r["quantity"], r["price"]),
                )
                conn.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                    (r["quantity"], r["product_id"]),
                )

            # Clear cart
            conn.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))

            # Mark order complete
            conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("COMPLETED", order_id))

            conn.execute("COMMIT")
            return order_id, None
        except Exception as e:
            conn.execute("ROLLBACK")
            return None, str(e)
        finally:
            conn.isolation_level = ""
    finally:
        conn.close()


def list_orders(user_id: int):
    """Return a list of order summaries for the user, newest first."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT order_id, order_date, total_amount, status
            FROM orders
            WHERE user_id = ?
            ORDER BY datetime(order_date) DESC, order_id DESC
            """,
            (user_id,),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
