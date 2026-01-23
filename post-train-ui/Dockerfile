FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir \
    torch==2.0.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    streamlit \
    transformers>=4.45.0 \
    tokenizers>=0.19.0 \
    sentencepiece \
    "protobuf<5" \
    huggingface_hub>=0.25.0 \
    einops \
    blinker \
    cachetools \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY . /app

EXPOSE 8501

CMD ["streamlit","run","app.py","--server.address=0.0.0.0","--server.baseUrlPath=train","--server.enableXsrfProtection=false"]