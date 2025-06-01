# Chatbot with RAG（Retrieval-Augmented Generation）Side Project

## 專案簡介

本專案是一個結合 RAG（檢索增強生成技術）的聊天機器人，目標是提供即時且精確的旅遊/知識查詢服務。  
使用者可透過 Gradio 網頁介面互動，後端結合 Llama 3（Ollama）、ChromaDB 向量資料庫、SQLite3 資料庫，實現高效率知識檢索與生成。

---

## 主要功能

- 支援自然語言旅遊/知識查詢
- 檢索增強生成（RAG）架構：可查詢本地向量資料庫後再產生回應
- SQLite3 資料庫紀錄聊天歷史
- Gradio Web UI，友善互動
- Python 程式架構，易於維護與擴充

---

## 使用技術

- Python 3.10+
- Gradio
- Ollama / Llama 3（本地部署）
- ChromaDB（向量資料庫）
- SQLite3 (聊天歷史紀錄)
- requests（API 整合）

---

## 安裝與執行步驟

### 1. 環境準備

請先安裝 Python 3.10 或以上版本，建議建立虛擬環境（venv）。

### 2. 安裝套件

```bash
pip install -r requirements.txt
````

（如未提供 `requirements.txt`，請手動安裝 gradio、chromadb、requests 等必要套件）

### 3. 部署 Llama 及 ChromaDB

* 依 Ollama 或 Llama 官方說明下載模型
* 啟動向量資料庫（ChromaDB）

### 4. 啟動聊天機器人

```bash
python app.py
```

* 或依專案實際架構執行主程式

### 5. 開啟瀏覽器，進入 Gradio 顯示的網址進行互動

---

## 專案結構範例

```text
├── app.py               # 主程式
├── embed.py             # 向量化/資料處理模組
├── rag_retrieve.py      # RAG 檢索邏輯
├── requirements.txt     # 依賴套件清單
├── .gitignore
└── README.md
```

---

## 注意事項

* 若有私密或大型資料（如 .db），請務必加入 `.gitignore`
* 本專案僅作自我學習、展示用途，請勿直接用於商業用途
* 本專案仍有許多不足之處，將會慢慢去做修正

---

## 貢獻方式

歡迎提出 Issue、PR 或討論建議！
有任何問題請透過 GitHub Issues 聯絡。

---

