import os
from pathlib import Path
import argparse
import math

PAGE_CHAR_LIMIT = 350  # Adjust for page size

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>故事绘本</title>
    <style>
        body {
            background: linear-gradient(135deg, #f8fafc 0%, #e0f7fa 100%);
            font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 700px;
            margin: 40px auto;
            background: #fff;
            border-radius: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .page {
            padding: 48px 36px 60px 36px;
            min-height: 420px;
            font-size: 2.2em;
            line-height: 1.7;
            text-align: justify;
            background: linear-gradient(120deg, #fceabb 0%, #f8b500 100%);
            color: #2d2d2d;
            border-bottom: 2px solid #f8fafc;
        }
        .page:last-child {
            border-bottom: none;
        }
        .page-num {
            text-align: right;
            font-size: 1.1em;
            color: #888;
            margin-top: 12px;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            color: #f57c00;
            margin-bottom: 0.5em;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>主题公园的故事</h1>
        {pages}
    </div>
</body>
</html>
'''

def split_into_pages(text, char_limit=PAGE_CHAR_LIMIT):
    # Split by Chinese period or paragraph, but keep sentences together
    import re
    sentences = re.split(r'(。|！|？|\!|\?|\n)', text)
    # Recombine sentences with their punctuation
    chunks = []
    buf = ''
    for i in range(0, len(sentences)-1, 2):
        chunk = sentences[i] + sentences[i+1]
        if len(buf) + len(chunk) > char_limit and buf:
            chunks.append(buf.strip())
            buf = ''
        buf += chunk
    if buf.strip():
        chunks.append(buf.strip())
    return chunks

def main():
    parser = argparse.ArgumentParser(description='Convert story text to beautiful HTML pages.')
    parser.add_argument('input_txt', help='Input story text file')
    parser.add_argument('output_html', help='Output HTML file')
    args = parser.parse_args()

    with open(args.input_txt, encoding='utf-8') as f:
        story = f.read()
    # Remove any leading comments or non-story lines
    story = '\n'.join([line for line in story.splitlines() if not line.strip().startswith('//') and line.strip()])
    pages = split_into_pages(story)
    html_pages = []
    for idx, page in enumerate(pages, 1):
        html_pages.append(f'<div class="page">{page}<div class="page-num">第 {idx} 页</div></div>')
    html = HTML_TEMPLATE.format(pages='\n'.join(html_pages))
    with open(args.output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Wrote {len(pages)} pages to {args.output_html}")

if __name__ == '__main__':
    main()
