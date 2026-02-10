import streamlit as st
import fitz
import requests
from io import BytesIO

st.set_page_config(page_title="PDF→RAG字段化", layout="centered")
st.title("🚀 PDF 自動字段化＆RAG準備（単独ファイルダウンロード）")

# ------------------------
# 上传限制
# ------------------------
MAX_UPLOAD = 10  # 每次最多上传 10 个 PDF

uploaded_files = st.file_uploader(
    "📄 アップロード PDF（最大10個）",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > MAX_UPLOAD:
        st.warning(f"⚠️ 一度にアップロードできるPDFは最大 {MAX_UPLOAD} 件です")
        st.stop()

    for pdf_file in uploaded_files:
        st.write(f"📄 処理中: {pdf_file.name}")

        # PDF → 文本
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        pdf_text = "\n".join([page.get_text("text") for page in doc]).strip()
        if not pdf_text:
            st.warning(f"⚠️ PDF 为空: {pdf_file.name}")
            continue

        # LLM 提取字段
        prompt = f"""
企業ID：
請求書番号：
領収書番号：
支払い日：
支払い方法：
会社ID：
発行日：
支払い期限：
請求金額：
消費税：
合計金額：
支払い条件：
請求先：
登録番号：
注文番号：
注文日：
注文者：
内容：

テキスト：
{pdf_text}

⚠️ 必ずこのフォーマットで出力してください
"""
        payload = {"model": "qwen2.5:7b-instruct", "prompt": prompt, "max_tokens": 500, "temperature": 0}
        try:
            r = requests.post("http://localhost:11434/v1/completions", json=payload)
            r.raise_for_status()
            result = r.json()
            standardized_text = result.get("completion", "").strip()
        except Exception as e:
            st.error(f"LLM 抽出失敗: {e}")
            continue

        if standardized_text:
            # 每个 PDF 生成独立下载文件
            st.download_button(
                label=f"📥 ダウンロード {pdf_file.name.replace('.pdf', '.txt')}",
                data=standardized_text,
                file_name=f"{pdf_file.name.replace('.pdf', '.txt')}",
                mime="text/plain"
            )
        else:
            st.warning(f"⚠️ LLM 返却なし: {pdf_file.name}")
