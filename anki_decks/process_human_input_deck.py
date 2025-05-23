import argparse
import csv
import re
from pypinyin import lazy_pinyin, Style

def sentence_to_pinyin(sentence):
    return ' '.join(lazy_pinyin(sentence, style=Style.TONE))

def parse_cedict(path):
    dictionary = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            match = re.match(r"(\S+)\s+(\S+)\s+\[(.+?)\]\s+/(.+)/", line)
            if match:
                trad, simp, pinyin, eng = match.groups()
                translations = eng.split('/')
                # Always take the first definition, even if it's a 'variant of' or 'old variant' etc.
                cleaned = re.split(r'[;(\[]', translations[0])[0].strip()
                dictionary[simp] = (cleaned, pinyin)
    return dictionary

def get_meaning_and_pinyin(word, cedict):
    if word in cedict:
        meaning, _ = cedict[word]
        word_pinyin = sentence_to_pinyin(word)
        return meaning, word_pinyin
    chars = list(word)
    meanings = []
    for char in chars:
        if char in cedict:
            m, _ = cedict[char]
            meanings.append(m)
    meaning = "; ".join(meanings) if meanings else ""
    word_pinyin = sentence_to_pinyin(word)
    return meaning, word_pinyin

def bold_word_in_sentence(word, sentence):
    # Only bold the first occurrence
    return sentence.replace(word, f"<b>{word}</b>", 1) if word in sentence else sentence

def main():
    parser = argparse.ArgumentParser(description="Process a human-generated Mandarin deck.")
    parser.add_argument('--input-file', '-i', required=True, help='Input file with word, sample sentence, and translation')
    parser.add_argument('--output-file', '-o', default='anki_worddeck.txt', help='Output TSV file')
    parser.add_argument('--cedict', default='cedict_ts.u8', help='Path to CC-CEDICT file')
    args = parser.parse_args()

    cedict = parse_cedict(args.cedict)

    with open(args.input_file, 'r', encoding='utf-8') as fin, open(args.output_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin, delimiter='\t')
        writer = csv.writer(fout, delimiter='\t')
        for row in reader:
            if len(row) < 3:
                continue
            word, sample_cn, sample_en = row[:3]
            meaning, word_pinyin = get_meaning_and_pinyin(word, cedict)
            sample_cn_bolded = bold_word_in_sentence(word, sample_cn) if sample_cn else ''
            sample_pinyin = sentence_to_pinyin(sample_cn) if sample_cn else ''
            writer.writerow([
                word, meaning, word_pinyin,
                sample_cn_bolded, sample_en, sample_pinyin
            ])
    print(f"Done! Output saved to {args.output_file}")

if __name__ == '__main__':
    main()