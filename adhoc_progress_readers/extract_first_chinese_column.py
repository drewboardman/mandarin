import sys
import os

if len(sys.argv) < 2:
    print("Usage: python extract_first_chinese_column.py <input_file.txt>")
    sys.exit(1)

input_path = sys.argv[1]
base, ext = os.path.splitext(input_path)
output_path = base + "_first_col.csv"

first_words = []
with open(input_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        cols = line.rstrip('\n').split('\t')
        if cols:
            first_words.append(cols[0])

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(','.join(first_words) + '\n')

print(f"Extracted {len(first_words)} words to {output_path}")
