FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libgomp1 \
    poppler-utils \
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
    PyMuPDF \
    requests \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY . /app

EXPOSE 8501

CMD ["streamlit","run","app.py","--server.address=0.0.0.0","--server.baseUrlPath=convert","--server.enableXsrfProtection=false"]