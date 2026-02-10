import streamlit as st
import fitz
import requests
import zipfile
import io

# =========================
# 基础设置
# =========================
st.set_page_config(page_title="PDF→RAG字段化", layout="centered")
st.title("🚀 PDF 自動字段化＆RAG準備")

MAX_UPLOAD = 10
OLLAMA_API = "http://ollama:11434/v1/completions"

# =========================
# 上传区
# =========================
uploaded_files = st.file_uploader(
    "📄 アップロード PDF（最大10個）",
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

    st.subheader("📂 選択されたファイル")
    for f in uploaded_files:
        st.write("-", f.name)

    progress = st.progress(0)
    total = len(uploaded_files)

    results = {}

    for i, pdf_file in enumerate(uploaded_files):

        st.markdown("---")
        st.write(f"📄 処理中: {pdf_file.name}")

        progress.progress(i / total)

        # =====================
        # PDF → TEXT
        # =====================
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            pdf_text = "\n".join(
                [page.get_text("text") for page in doc]
            ).strip()
        except Exception as e:
            st.error(f"❌ PDF解析失敗: {e}")
            continue

        if not pdf_text:
            st.warning(f"⚠️ 空PDF: {pdf_file.name}")
            continue

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

⚠️ 必ずこのフォーマットで出力
"""

        payload = {
            "model": "qwen2.5:7b-instruct",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0
        }

        # =====================
        # LLM
        # =====================
        try:
            with st.spinner("🤖 LLM抽出中..."):

                r = requests.post(
                    OLLAMA_API,
                    json=payload,
                    timeout=600
                )

                r.raise_for_status()
                result = r.json()

                text = result.get("completion", "").strip()

        except Exception as e:
            st.error(f"❌ LLM失敗: {e}")
            continue

        if text:
            results[pdf_file.name.replace(".pdf", ".txt")] = text
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

        # ZIP 打包
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
