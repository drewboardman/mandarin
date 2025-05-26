import argparse
import csv
from pypinyin import lazy_pinyin, Style

def sentence_to_pinyin(sentence):
    return ' '.join(lazy_pinyin(sentence, style=Style.TONE))

def main():
    parser = argparse.ArgumentParser(description="Add pinyin column to an existing Mandarin deck.")
    parser.add_argument('--input-file', '-i', required=True, help='Input TSV file with at least 4 columns (word, meaning, pinyin, sentence, ...)')
    parser.add_argument('--output-file', '-o', default='deck_with_pinyin.txt', help='Output TSV file')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as fin, open(args.output_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin, delimiter='\t')
        writer = csv.writer(fout, delimiter='\t')
        for row in reader:
            if len(row) < 4:
                continue
            sentence_cn = row[3]
            sentence_pinyin = sentence_to_pinyin(sentence_cn) if sentence_cn else ''
            writer.writerow(row + [sentence_pinyin])
    print(f"Done! Output saved to {args.output_file}")

if __name__ == '__main__':
    main()
