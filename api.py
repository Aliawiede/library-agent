
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import traceback

from server.tools import find_books, create_order, order_status, restock_book, update_price, inventory_summary
from server.agent import build_agent
from server.chat_db import list_sessions, create_session, load_session_messages, save_message

app = FastAPI(title="Library Desk Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = build_agent()


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]


class OrderItem(BaseModel):
    isbn: str
    qty: int


class OrderRequest(BaseModel):
    customer_id: int
    items: List[OrderItem]


class RestockRequest(BaseModel):
    isbn: str
    qty: int


class UpdatePriceRequest(BaseModel):
    isbn: str
    price: float


def extract_text(data: Any) -> str:
    if isinstance(data, str):
        return data.strip()
    if isinstance(data, dict):
        if "output" in data:
            return str(data["output"]).strip()
        if "messages" in data:
            for m in data["messages"]:
                if "content" in m and not str(m["content"]).startswith("{"):
                    return str(m["content"]).strip()
    return str(data).strip()


def clean_text(text: str) -> str:
    if not text:
        return "No response generated."
    text = text.strip()
    if text.startswith(("{", "[")):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "result" in parsed:
                return str(parsed["result"])
        except json.JSONDecodeError:
            return text
    return text


def save_chat_message(session_id: str, role: str, content: str):
    save_message(session_id, role, content)


@app.get("/")
def root():
    return {"status": "running", "chat": "/chat", "sessions": "/sessions", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatMessage):
    try:
        session_id = request.session_id or str(create_session())
        save_chat_message(session_id, "user", request.message)

        agent_output = agent.invoke({"input": request.message})
        reply = clean_text(extract_text(agent_output))
        save_chat_message(session_id, "assistant", reply)

        return ChatResponse(response=reply, session_id=session_id)
    except Exception as e:
        traceback.print_exc()
        return ChatResponse(response=f"Error: {e}", session_id=request.session_id or "error")


@app.get("/sessions", response_model=List[int])
def get_sessions():
    return list_sessions() or []


@app.post("/sessions/new")
def new_session():
    return {"session_id": create_session()}


@app.get("/sessions/{session_id}/messages", response_model=SessionResponse)
def session_messages(session_id: str):
    return SessionResponse(session_id=session_id, messages=load_session_messages(session_id))


@app.get("/books")
def api_books(query: str, by: str = "title"):
    try:
        result = find_books.invoke({"q": query, "by": by})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders")
def api_orders(order: OrderRequest):
    try:
        items = [{"isbn": i.isbn, "qty": i.qty} for i in order.items]
        result = create_order.invoke({"customer_id": order.customer_id, "items": items})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}")
def api_order_status(order_id: int):
    try:
        result = order_status.invoke({"order_id": order_id})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restock")
def api_restock(req: RestockRequest):
    try:
        result = restock_book.invoke({"isbn": req.isbn, "qty": req.qty})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update_price")
def api_update_price(req: UpdatePriceRequest):
    try:
        result = update_price.invoke({"isbn": req.isbn, "price": req.price})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/inventory_summary")
def api_inventory_summary():
    try:
        result = inventory_summary.invoke({})
        return {"result": extract_text(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

