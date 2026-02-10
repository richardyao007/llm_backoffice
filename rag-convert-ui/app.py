import streamlit as st
import fitz
import requests

# =========================
# 基础设置
# =========================
st.set_page_config(page_title="PDF→RAG字段化", layout="centered")
st.title("🚀 PDF 自動字段化＆RAG準備（単独ファイルダウンロード）")

MAX_UPLOAD = 10

# ⚠️ Docker 内访问 ollama 必须用服务名
OLLAMA_API = "http://ollama:11434/v1/completions"

# =========================
# 上传
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
        st.warning(f"⚠️ 一度にアップロードできるPDFは最大 {MAX_UPLOAD} 件です")
        st.stop()

    st.write("📂 選択されたファイル:")
    for f in uploaded_files:
        st.write("-", f.name)

    progress = st.progress(0)
    total = len(uploaded_files)

    for i, pdf_file in enumerate(uploaded_files):

        st.markdown(f"---")
        st.write(f"📄 処理中: {pdf_file.name}")

        # 更新进度条
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
            st.warning(f"⚠️ PDF 为空: {pdf_file.name}")
            continue

        # =====================
        # 构造 Prompt
        # =====================
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

        payload = {
            "model": "qwen2.5:7b-instruct",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0
        }

        # =====================
        # LLM 调用
        # =====================
        try:
            with st.spinner("🤖 LLM 抽出中..."):

                r = requests.post(
                    OLLAMA_API,
                    json=payload,
                    timeout=600   # 防止无限卡死
                )

                r.raise_for_status()
                result = r.json()

                standardized_text = result.get(
                    "completion", ""
                ).strip()

        except Exception as e:
            st.error(f"❌ LLM 抽出失敗: {e}")
            continue

        # =====================
        # 下载
        # =====================
        if standardized_text:

            st.download_button(
                label=f"📥 ダウンロード {pdf_file.name.replace('.pdf', '.txt')}",
                data=standardized_text,
                file_name=pdf_file.name.replace(".pdf", ".txt"),
                mime="text/plain"
            )

        else:
            st.warning(f"⚠️ LLM 返却なし: {pdf_file.name}")

    progress.progress(1.0)
    st.success("🎉 全てのPDF処理が完了しました！")
