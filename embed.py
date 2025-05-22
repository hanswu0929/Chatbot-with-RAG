import glob, os, requests, chromadb

CHUNK_SIZE = 400         # 每段最大字數
KNOW_PATH  = "knowledge" # 你的知識檔資料夾
CHROMA_DIR = "chroma_db" # 向量資料庫資料夾

def chunk_text(text, size):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ollama_embed_text(text_list):
    url = "http://localhost:11434/api/embeddings"
    results = []
    for text in text_list:
        print("送出字串：", repr(text))  # debug
        if not text.strip():           # 跳過空白
            print("⚠️  跳過空白段落")
            continue
        response = requests.post(url, json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        data = response.json()
        print("API回傳內容：", data)
        if "embedding" not in data or not data["embedding"]:
            print("⚠️  無法產生向量，送出的內容為：", repr(text))
            continue
        results.append(data["embedding"])
    return results


def main():
    docs = []
    for file in glob.glob(os.path.join(KNOW_PATH, "*.txt")):
        with open(file, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            docs.extend(chunk_text(raw, CHUNK_SIZE))
    
    embeds = ollama_embed_text(docs)
    print(f"已完成向量化：共 {len(docs)} 段")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("knowledge")
    ids = [str(i) for i in range(len(docs))]
    col.add(documents=docs, embeddings=embeds, ids=ids)
    print(f"✅  已匯入 {len(docs)} 個 chunk → chroma_db/")
    # 新增
    print("docs:", docs)
    print("embeds:", embeds)


if __name__ == "__main__":
    main()