import requests
import gradio as gr

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
        return f"抱歉，發生錯誤 : {str(e)}"
    

def chatgpt_clone(user_input, history, max_rounds):
    if not isinstance(history, list):
        history = []
    
    # 組裝 messages 給模型用
    messages = [{"role":"system", "content":"你是一個旅遊問答助手。你的回答風格是友好的、口語化的。"}]

    for user_msg, assistant_msg in history:
        messages.append({"role":"user", "content": user_msg})
        messages.append({"role":"assistant", "content":assistant_msg})
    
    messages.append({"role":"user", "content":user_input})

    # 呼叫模型
    output = call_local_model_with_messages(messages)

    # 更新對話紀錄
    history.append((user_input, output))

    # 限制只保留最近 max_round 輪（每輪包含一問一答）
    history = history[-int(max_rounds):]

    return history, history

with gr.Blocks() as block:
    gr.Markdown("""<h1><center>旅遊助手</center></h1>""")

    round_selector = gr.Slider(1, 10, value=5, step=1, label="保留對話輪數")
    chatbot = gr.Chatbot()
    message = gr.Textbox(placeholder="請輸入您的旅遊相關問題...")
    state = gr.State([])
    # 聊天紀錄是透過 Python 中的變數 history 來傳遞的，而 gr.State 就像是一個「儲物箱」，幫你在按鈕之間維持這份聊天紀錄。
    submit = gr.Button("送出")

    def clear_input():
        return ""
    
    submit.click(chatgpt_clone, inputs=[message, state, round_selector], outputs=[chatbot, state])
    submit.click(clear_input, inputs=[], outputs=[message])

block.launch(share=True)

# abcdefg