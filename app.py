import requests
import gradio as gr

API_BASE_URL = "http://localhost:8000"


def api_request(endpoint, method="GET", data=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            r = requests.get(url, params=data)
        elif method == "POST":
            r = requests.post(url, json=data)
        elif method == "DELETE":
            r = requests.delete(url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_sessions():
    result = api_request("/sessions")
    return [str(s) for s in result] if isinstance(result, list) else []

def create_session():
    result = api_request("/sessions/new", method="POST")
    return str(result.get("session_id")) if isinstance(result, dict) else None

def load_messages(session_id):
    if not session_id:
        return []
    result = api_request(f"/sessions/{session_id}/messages")
    if isinstance(result, dict) and "messages" in result:
        return [{"role": m["role"], "content": m["content"]} for m in result["messages"]]
    return []


def chat_response(user_msg, history, session_id):
    if not user_msg:
        return "", history

    if session_id == "New Session" or not session_id:
        session_id = create_session()
        if not session_id:
            history.append({"role": "assistant", "content": "Failed to create a new session."})
            return "", history

    payload = {"message": user_msg, "session_id": session_id}
    result = api_request("/chat", method="POST", data=payload)
    reply = result.get("response", f"Error: {result.get('error', 'No response')}")

    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": reply})

    return "", history


def select_session(session_id):
    if not session_id or session_id == "New Session":
        return []
    return load_messages(session_id)

def handle_new_session():
    sid = create_session()
    if sid:
        sessions = ["New Session"] + get_sessions()
        messages = []
        return sessions, sid, messages
    return get_sessions(), "New Session", []

sessions = ["New Session"] + get_sessions()

with gr.Blocks(title="Library Desk Agent") as demo:
    gr.Markdown("# Library Desk Agent")
    gr.Markdown("Manage your library sessions and chat with the assistant.")

    with gr.Row():
        with gr.Column(scale=1):
            session_dropdown = gr.Dropdown(
                label="Session",
                choices=sessions,
                value="New Session",
                interactive=True,
                allow_custom_value=True
            )
            new_session_btn = gr.Button("Start New Session", variant="primary")

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(type="messages", height=400, value=[])
            msg_box = gr.Textbox(placeholder="Type your message...")
            send_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")


    session_dropdown.change(select_session, inputs=[session_dropdown], outputs=[chatbot])
    new_session_btn.click(handle_new_session, outputs=[session_dropdown, session_dropdown, chatbot])
    msg_box.submit(chat_response, inputs=[msg_box, chatbot, session_dropdown], outputs=[msg_box, chatbot])
    send_btn.click(chat_response, inputs=[msg_box, chatbot, session_dropdown], outputs=[msg_box, chatbot])
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg_box])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
