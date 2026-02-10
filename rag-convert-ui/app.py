import streamlit as st
import fitz
import requests
import zipfile
import io
import json

# =========================
# 基础设置
# =========================
st.set_page_config(page_title="PDF→RAG字段化", layout="centered")
st.title("🚀 PDF 自動字段化＆RAG準備（Streaming版）")

MAX_UPLOAD = 10
OLLAMA_API = "http://ollama:11434/api/generate"
MODEL = "qwen2.5:7b-instruct"

# =========================
# 分块函数
# =========================
def split_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# =========================
# 上传
# =========================
uploaded_files = st.file_uploader(
    "📄 PDFアップロード（最大10件）",
    type=["pdf"],
    accept_multiple_files=True
)

# =========================
# 主流程
# =========================
if uploaded_files:

    if len(uploaded_files) > MAX_UPLOAD:
        st.warning(f"⚠️ 最大 {MAX_UPLOAD} 件まで")
        st.stop()

    results = {}
    progress = st.progress(0)
    total = len(uploaded_files)

    for i, pdf_file in enumerate(uploaded_files):

        st.markdown("---")
        st.write(f"📄 処理中: {pdf_file.name}")

        progress.progress(i / total)

        # ========= PDF读取 =========
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            pdf_text = "\n".join(
                [page.get_text("text") for page in doc]
            ).strip()
        except Exception as e:
            st.error(f"❌ PDF解析失敗: {e}")
            continue

        if not pdf_text:
            st.warning("⚠️ 空PDF（スキャンPDFの可能性）")
            continue

        chunks = split_text(pdf_text)

        output_box = st.empty()
        full_output = ""

        # ========= LLM处理 =========
        for idx, chunk in enumerate(chunks):

            prompt = f"""
以下の項目を必ず抽出してください。
存在しない場合は「不明」と記載。

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
{chunk}
"""

            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0
                }
            }

            try:
                with requests.post(
                    OLLAMA_API,
                    json=payload,
                    stream=True,
                    timeout=600
                ) as r:

                    for line in r.iter_lines():

                        if not line:
                            continue

                        data = json.loads(line.decode("utf-8"))

                        token = data.get("response", "")

                        if token:
                            full_output += token
                            output_box.markdown(full_output)

            except Exception as e:
                st.error(f"❌ LLM失敗: {e}")
                continue

        # ========= 结果 =========
        if full_output.strip():

            txt_name = pdf_file.name.replace(".pdf", ".txt")

            results[txt_name] = full_output

            st.success(f"✅ 完成: {pdf_file.name}")

        else:
            st.warning(f"⚠️ LLM返却なし: {pdf_file.name}")

    progress.progress(1.0)

    # =========================
    # 下载区
    # =========================
    if results:

        st.markdown("---")
        st.subheader("📦 ダウンロード")

        # 单文件下载
        for filename, content in results.items():

            st.download_button(
                label=f"📥 {filename}",
                data=content,
                file_name=filename,
                mime="text/plain"
            )

        # ZIP下载
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for filename, content in results.items():
                z.writestr(filename, content)

        st.download_button(
            label="📦 一括ZIPダウンロード",
            data=zip_buffer.getvalue(),
            file_name="rag_results.zip",
            mime="application/zip"
        )

        st.success("🎉 全処理完了！")
