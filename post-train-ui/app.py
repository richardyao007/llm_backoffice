import streamlit as st
import subprocess
from pathlib import Path

# =========================
# ページ設定
# =========================

st.set_page_config(page_title="モデル工場", layout="centered")
st.title("🚀 ワンクリックモデル工場（H2O → GGUF → Ollama）")

# =========================
# パス設定
# =========================

LLAMA_DIR = Path("/llama.cpp")
MODEL_DIR = Path("/models/blobs")
H2O_MODELS_DIR = Path("/h2o-output/output/user")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 前置チェック
# =========================

convert_script = LLAMA_DIR / "convert_hf_to_gguf.py"
quantize_bin = LLAMA_DIR / "build" / "bin" / "llama-quantize"

if not convert_script.exists():
    st.error("❌ convert_hf_to_gguf.py が見つかりません。llama.cpp のマウントと git pull を確認してください")
    st.stop()

if not quantize_bin.exists():
    st.error(f"❌ 量子化ツール {quantize_bin} が見つかりません。コンテナ内で make または cmake build を実行してください")
    st.stop()

if not H2O_MODELS_DIR.exists():
    st.error("❌ H2O モデルディレクトリが見つかりません")
    st.stop()

model_dirs = sorted([p for p in H2O_MODELS_DIR.iterdir() if p.is_dir()])
if not model_dirs:
    st.warning("⚠️ H2O 訓練済みモデルがありません")
    st.stop()

# =========================
# UI 入力
# =========================

hf_model_dir = st.selectbox(
    "1️⃣ H2O モデルを選択",
    options=model_dirs,
    format_func=lambda p: p.name,
)

ollama_name = st.text_input("2️⃣ Ollama モデル名", placeholder="test-backoffice-qwen2")

quant_type = st.selectbox(
    "3️⃣ 量子化タイプ",
    ["q4_K_M", "q8_0"],
    index=0,
)

# =========================
# 実行ボタン
# =========================

if st.button("🚀 変換＆Ollama登録を開始", use_container_width=True):

    if not ollama_name.strip():
        st.error("❌ モデル名を入力してください")
        st.stop()

    config_path = hf_model_dir / "config.json"
    if not config_path.exists():
        st.error("❌ config.json がありません")
        st.stop()

    f16_gguf = MODEL_DIR / f"{ollama_name}-f16.gguf"
    final_gguf = MODEL_DIR / f"{ollama_name}.gguf"

    if final_gguf.exists():
        st.error("❌ ファイルが既に存在します。別の名前を使用してください")
        st.stop()

    # ---- 1. f16 GGUF へ変換 ----
    st.write("f16 GGUF に変換中...")
    convert_cmd = [
        "python",
        str(convert_script),
        str(hf_model_dir),
        "--outfile", str(f16_gguf),
        "--outtype", "f16",
        "--verbose",
    ]

    try:
        process = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = []
        for line in iter(process.stdout.readline, ''):
            st.text(line.strip())
            output.append(line)
        process.wait()
        if process.returncode != 0:
            st.error("変換に失敗しました！\n" + "\n".join(output[-20:]))
            st.stop()
    except Exception as e:
        st.error(f"変換エラー: {e}")
        st.stop()

    st.success("✅ f16 GGUF 変換完了")

    # ---- 2. 量子化 ----
    st.write(f"{quant_type} に量子化中...")
    try:
        subprocess.run([str(quantize_bin), str(f16_gguf), str(final_gguf), quant_type], check=True)
    except Exception as e:
        st.error(f"量子化に失敗しました: {e}")
        st.stop()

    st.success("✅ 量子化完了")

    # ---- 3. Modelfile 作成 ----
#     modelfile_content = f"""FROM /root/.ollama/models/blobs/{final_gguf.name}
# TEMPLATE \"\"\"
# {{{{ if .System }}}}<|im_start|>system
# {{{{ .System }}}}<|im_end|>
# {{{{ end }}}}
# <|im_start|>user
# {{{{ .Prompt }}}}<|im_end|>
# <|im_start|>assistant
# \"\"\"
# PARAMETER stop "<|im_end|>"
# PARAMETER stop "<|im_start|>"
# PARAMETER temperature 0.7
# PARAMETER top_p 0.9
# """

    modelfile_content = f"""FROM /root/.ollama/models/blobs/{final_gguf.name}
TEMPLATE """{{"""{{""" if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.05
"""

    modelfile_path = MODEL_DIR / f"{ollama_name}.Modelfile"
    modelfile_path.write_text(modelfile_content, encoding="utf-8")

    # ---- 4. Ollama 登録用コマンド表示 ----
    ollama_cmd = (
        f"docker exec ollama "
        f"ollama create {ollama_name} "
        f"-f /root/.ollama/models/blobs/{ollama_name}.Modelfile"
    )

    st.success("✅ GGUF と Modelfile の生成が完了しました")

    st.markdown("### 📌 ホストマシンで以下のコマンドを実行して登録を完了してください：")
    st.code(ollama_cmd, language="bash")

    st.markdown("### ▶ 登録後、次のコマンドで確認・実行できます：")
    st.code(
        f"docker exec ollama ollama list\ndocker exec ollama ollama run {ollama_name}",
        language="bash"
    )