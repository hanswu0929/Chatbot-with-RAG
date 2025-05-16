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
    

def chatgpt_clone(user_input, history_all, max_rounds):
    # 更新全部聊天歷史
    if not isinstance(history_all, list):
        history_all = []
    
    # 擴增全部聊天歷史
    history_all.append((user_input, ""))

    # 傳給模型的對話數
    history_context = history_all[-int(max_rounds):]

    # 組裝 messages 給模型用
    messages = [{"role":"system", "content":"你是一個旅遊問答助手。你的回答風格是友好的、口語化的。"}]

    for user_msg, assistant_msg in history_context:
        messages.append({"role":"user", "content": user_msg})
        if assistant_msg:
            messages.append({"role":"assistant", "content":assistant_msg}) 
    messages.append({"role":"user", "content":user_input})

    # 呼叫模型
    output = call_local_model_with_messages(messages)

    history_all[-1] = (user_input, output)

    return history_all, history_all

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