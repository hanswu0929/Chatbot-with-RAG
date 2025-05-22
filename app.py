import requests
import sqlite3
import gradio as gr
from rag_retrieve import build_rag_prompt

DATABASE = "history.db"

# 資料庫連線
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 儲存一筆聊天問答到資料庫
def save_to_db(user_msg, assistant_msg):
    conn = get_db()
    db = conn.cursor()
    db.execute("""
        INSERT INTO chat_history (user_message, assistant_message) VALUES (?, ?)
    """, (user_msg, assistant_msg))
    conn.commit()
    conn.close()

# 載入所有歷史紀錄
def load_all_history():
    conn = get_db()
    db = conn.cursor()
    db.execute("SELECT id, user_message, assistant_message, timestamp FROM chat_history ORDER BY id ASC")
    rows = db.fetchall() # 這裡是 list of sqlite3.Row
    conn.close()

    history = [dict(row) for row in rows] # 轉成 list of dict
    return history

def call_local_model_with_messages(messages):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json = {
                "model":"gemma3:1b",
                "messages":messages,
                "stream": False
            }
        )
        result = response.json()
        return result["message"]["content"].strip()
    except Exception as e:
        print(f"模型呼叫錯誤：{e}")
        return f"抱歉，發生錯誤 : {str(e)}"
    
# 聊天主流程（history 只保留最近 N 輪，全部問答永久進 DB）
def chatgpt_clone(user_input, history, max_rounds):
    
    # 更新全部聊天歷史
    if isinstance(history, list):
        history = []
    
    # 1. 利用 RAG 查詢並組 Prompt
    rag_prompt = build_rag_prompt(user_input)

    # 2. 把 prompt 當作 system message 傳給模型
    message = [
        {"role": "system", "content": rag_prompt}
    ]

    # 3. 呼叫 LLM 取得回應（call_local_model_with_messages）
    output = call_local_model_with_messages(message)

    # 4. 儲存與顯示紀錄
    save_to_db(user_input, output)
    history.append((user_input, output))
    history = history[-int(max_rounds):]

    # 5. 給 chatbot 轉換成 messages 格式
    chatbot_msgs = []
    for u, a in history:
        chatbot_msgs += [
            {"role": "user", "content": u},
            {"role": "assistant", "content": a},
        ]
    
    return chatbot_msgs, history

# 顯示所有歷史聊天（以 Markdown 呈現）
def show_full_history():
    rows = load_all_history()
    if not rows:
        return "(目前尚無任何聊天紀錄)"
    text = ""
    for row in rows:
        text += f"**{row['id']}. 使用者:**{row['user_message']}\n\n"
        text += f"** 助理:**{row['assistant_message']}\n\n"
        text += f"`{row['timestamp']}`\n\n---\n"
    return text

with gr.Blocks() as block:
    gr.Markdown("<h1><center>旅遊助手</center></h1>")

    round_selector = gr.Slider(1, 10, value=5, step=1, label="保留對話輪數")
    chatbot = gr.Chatbot(type="messages")
    message = gr.Textbox(placeholder="請輸入您的旅遊相關問題...")
    state = gr.State([]) # 存 session 對話紀錄（記憶體，不寫入 DB）

    # 聊天紀錄是透過 Python 中的變數 history 來傳遞的，而 gr.State 就像是一個「儲物箱」，幫你在按鈕之間維持這份聊天紀錄。
    submit = gr.Button("送出")
    clear_btn = gr.Button("清除本次對話")
    history_btn = gr.Button("顯示全部歷史紀錄")
    full_history_md = gr.Markdown(value="（點擊按鈕可顯示所有歷史聊天）")

    def clear_input():
        return ""
    
    submit.click(chatgpt_clone, inputs=[message, state, round_selector], outputs=[chatbot, state])
    submit.click(clear_input, inputs=[], outputs=[message])

    # 清除 session 聊天紀錄（但不會刪除永久資料庫）
    clear_btn.click(lambda: ([], []), None, outputs=[chatbot, state])

    # 顯示所有歷史紀錄
    history_btn.click(show_full_history, None, outputs=[full_history_md])

block.launch(share=True)