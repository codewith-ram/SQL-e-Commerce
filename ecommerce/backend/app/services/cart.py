from ..database.db import get_connection


def add_to_cart(user_id: int, product_id: int, quantity: int):
    conn = get_connection()
    try:
        # Ensure cart exists
        cur = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur = conn.execute("INSERT INTO carts (user_id) VALUES (?)", (user_id,))
            cart_id = cur.lastrowid
        else:
            cart_id = row["cart_id"]

        # If exists update quantity else insert
        cur = conn.execute(
            "SELECT cart_item_id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        )
        existing = cur.fetchone()
        if existing:
            new_qty = existing["quantity"] + quantity
            conn.execute(
                "UPDATE cart_items SET quantity = ? WHERE cart_item_id = ?",
                (new_qty, existing["cart_item_id"]),
            )
        else:
            conn.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (cart_id, product_id, quantity),
            )
        conn.commit()
    finally:
        conn.close()


def get_cart(user_id: int):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return {"items": [], "total": 0.0}
        cart_id = row["cart_id"]
        cur = conn.execute(
            """
            SELECT ci.cart_item_id, ci.product_id, p.name, p.price, ci.quantity,
                   (p.price * ci.quantity) AS subtotal
            FROM cart_items ci
            JOIN products p ON p.product_id = ci.product_id
            WHERE ci.cart_id = ?
            ORDER BY ci.cart_item_id
            """,
            (cart_id,),
        )
        items = [dict(r) for r in cur.fetchall()]
        total = sum(i["subtotal"] for i in items)
        return {"items": items, "total": total}
    finally:
        conn.close()


def clear_cart(user_id: int):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            conn.execute("DELETE FROM cart_items WHERE cart_id = ?", (row["cart_id"],))
            conn.commit()
    finally:
        conn.close()
