import chromadb
import requests
# 用來發送 HTTP 請求（這裡用於呼叫本地 Ollama API 取得向量）

CHROMA_DIR = "chroma_db"
TOP_K = 10  # 回傳最相關的前 K 筆資料

# 取得 Ollama embedding
def ollama_embed_text(text_list):
    url = "http://localhost:11434/api/embeddings"
    results = []
    for text in text_list:
        response = requests.post(url, json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        data = response.json()
        if "embedding" not in data or not data["embedding"]:
            print("⚠️  無法產生向量，送出的內容為：", repr(text))
            continue
        results.append(data["embedding"])
    return results


# 查詢與組合 Prompt
def build_rag_prompt(user_q: str) -> str:

    q_vec = ollama_embed_text([user_q])[0]
    # 本來 user_q 是一個字串，例如 "台灣有什麼旅遊景點？"
    # 要送進 embedding API，要變成 list 格式（因為 API 設計希望收到 list of str，不論你有幾個問題都這樣包)
    # 所以呼叫時寫成 ollama_embed_text([user_q])，這就是把單一字串包成一個只有一個元素的 list

    client = chromadb.PersistentClient(CHROMA_DIR)
    col = client.get_or_create_collection("knowledge")

    res = col.query(query_embeddings=[q_vec], n_results=TOP_K)
    chunks = res["documents"][0]

    print("檢索到的相關片段：", chunks)

    prompt = (
        "你是旅遊客服專員，僅可根據 <知識庫> 內容回答，若知識庫無相關資訊請回答「我不知道」。\n"
        "<知識庫>\n"
        + "\n".join([f"{i+1}. {ck}" for i, ck in enumerate(chunks)])
        + f"\n</知識庫>\n\n使用者問題{user_q}"
    )
    return prompt