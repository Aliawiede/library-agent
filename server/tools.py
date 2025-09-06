import sqlite3 
from contextlib import contextmanager
from typing import Any, List, Dict
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall

from server.config import Config
from server.logging import log, log_panel


def get_available_tools() -> List[BaseTool]:
    return [find_books, create_order, restock_book, update_price, order_status, inventory_summary]

def call_tool(tool_call: ToolCall) -> Any:
    tools_by_name = {tool.name: tool for tool in get_available_tools()}
    tool = tools_by_name[tool_call["name"]]
    response = tool.invoke(tool_call["args"])
    return ToolMessage(content=response, tool_call_id=tool_call["id"])

@contextmanager
def with_sql_cursor(readonly=True):
    conn = sqlite3.connect(Config.Path.DATABASE_PATH)
    cur = conn.cursor()
    try:
        yield cur 
        if not readonly: 
            conn.commit()
    except Exception:
        if not readonly:
            conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@tool(parse_docstring=True)
def find_books(q: str, by: str = "title") -> str:
    """
    Search for books by title or author.

    Args:
        q: Search term
        by: Field to search by ("title" or "author")

    Returns:
        String with matching books (isbn, title, author, stock)
    """
    if by not in ["title", "author"]:
        return "Invalid search field. Use 'title' or 'author'."

    log_panel(title="Find Books Tool", content=f"Searching for: {q} by {by}")

    try:
        with with_sql_cursor() as cur:
            cur.execute(f"SELECT isbn, title, author, stock FROM books WHERE {by} LIKE ?", (f"%{q}%",))
            rows = cur.fetchall()
        if not rows:
            return "No books found."
        return "\n".join([f"{r[0]} - {r[1]} by {r[2]} (Stock: {r[3]})" for r in rows])
    except Exception as e:
        log(f"[red]Error in find_books: {e}[/red]")
        return f"Error: {e}"


@tool(parse_docstring=True)
def create_order(customer_id: int, items: List[Dict[str, Any]]) -> str:  
    """
    Create a new order and update stock.

    Args:
        customer_id: ID of the customer
        items: List of dictionaries with 'isbn' and 'qty' keys

    Returns:
        New order ID and status
    """
    log_panel(title="Create Order Tool", content=f"Customer: {customer_id}, Items: {items}")

    try:
        with with_sql_cursor(readonly=False) as cur:
            cur.execute("INSERT INTO orders (customer_id) VALUES (?)", (customer_id,))
            order_id = cur.lastrowid

            for item in items:
                if not isinstance(item, dict):
                    return f"Error: Item must be a dictionary, got {type(item)}: {item}"
                if 'isbn' not in item or 'qty' not in item:
                    return f"Error: Item must have 'isbn' and 'qty' keys, got: {item}"
                
                cur.execute("INSERT INTO order_items (order_id, isbn, qty) VALUES (?, ?, ?)",
                            (order_id, item["isbn"], item["qty"]))
                cur.execute("UPDATE books SET stock = stock - ? WHERE isbn = ?",
                            (item["qty"], item["isbn"]))

        return f"Order created successfully (ID: {order_id})"
    except Exception as e:
        log(f"[red]Error in create_order: {e}[/red]")
        return f"Error creating order: {e}"


@tool(parse_docstring=True)
def restock_book(isbn: str, qty: int) -> str:
    """
    Increase stock for a specific book.

    Args:
        isbn: Book ISBN
        qty: Quantity to add

    Returns:
        Confirmation message
    """
    try:
        with with_sql_cursor(readonly=False) as cur:
            cur.execute("UPDATE books SET stock = stock + ? WHERE isbn = ?", (qty, isbn))
        return f"Stock for {isbn} increased by {qty}."
    except Exception as e:
        return f"Error restocking: {e}"

@tool(parse_docstring=True)
def update_price(isbn: str, price: float) -> str:
    """
    Update the price of a book.

    Args:
        isbn: Book ISBN
        price: New price

    Returns:
        Confirmation message
    """
    try:
        with with_sql_cursor(readonly=False) as cur:
            cur.execute("UPDATE books SET price = ? WHERE isbn = ?", (price, isbn))
        return f"Price for {isbn} updated to {price}."
    except Exception as e:
        return f"Error updating price: {e}"


@tool(parse_docstring=True)
def order_status(order_id: int) -> str:
    """
    Get details for a specific order.

    Args:
        order_id: Order ID

    Returns:
        Order details with items
    """
    try:
        with with_sql_cursor() as cur:
            cur.execute("SELECT id, customer_id, created_at FROM orders WHERE id = ?", (order_id,))
            order = cur.fetchone()

            if not order:
                return "Order not found."

            cur.execute("SELECT isbn, qty FROM order_items WHERE order_id = ?", (order_id,))
            items = cur.fetchall()

        return f"Order {order[0]} (Customer: {order[1]}, Created: {order[2]})\n" + \
               "\n".join([f"- {i[0]}: {i[1]} pcs" for i in items])
    except Exception as e:
        return f"Error fetching order status: {e}"

@tool(parse_docstring=True)
def inventory_summary() -> str:
    """
    Get list of books with low stock (< 5).

    Returns:
        String with low-stock books
    """
    try:
        with with_sql_cursor() as cur:
            cur.execute("SELECT isbn, title, stock FROM books WHERE stock < 5")
            rows = cur.fetchall()
        if not rows:
            return "All books are well-stocked."
        return "\n".join([f"{r[0]} - {r[1]} (Stock: {r[2]})" for r in rows])
    except Exception as e:
        return f"Error getting inventory summary: {e}"