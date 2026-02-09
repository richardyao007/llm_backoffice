#!/usr/bin/env bash

BASE_DIR=$(dirname "$0")

PDF_DIR="$BASE_DIR/pdf/1"
TXT_DIR="$BASE_DIR/txt/1"

mkdir -p "$TXT_DIR"

find "$PDF_DIR" -type f -name "*.pdf" | while IFS= read -r pdf_file
do
    filename=$(basename "$pdf_file")
    name="${filename%.pdf}"
    txt_file="$TXT_DIR/$name.txt"

    # 已存在就跳过
    if [ -f "$txt_file" ]; then
        echo "⏭ 跳过已存在: $txt_file"
        continue
    fi

    echo "📄 转换中: $pdf_file"

    curl -s -T "$pdf_file" http://localhost:9998/tika \
        -H "Accept: text/plain; charset=utf-8" \
        > "$txt_file"

    echo "✅ 完成: $txt_file"
done

echo "🎉 全部处理完成"
