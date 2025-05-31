import os
import sqlite3
yaml_output = []
import argparse

def parse_txt_words(txt_path):
    words = set()
    with open(txt_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            fields = line.strip().split('\t')
            if fields:
                word = fields[0].strip()
                if word:
                    words.add(word)
    return sorted(words)

def get_known_words(db_path, exclude_words):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT word FROM known_words')
    all_known = {row[0] for row in cur.fetchall()}
    conn.close()
    return sorted(all_known - set(exclude_words))

def main():
    parser = argparse.ArgumentParser(description='Extract new and known words from txt and output YAML.')
    parser.add_argument('txt_file', help='Input txt file')
    parser.add_argument('output_yaml', help='Output YAML file')
    args = parser.parse_args()

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../freq_words.db'))
    new_words = parse_txt_words(args.txt_file)
    known_words = get_known_words(db_path, new_words)

    with open(args.output_yaml, 'w', encoding='utf-8') as out:
        out.write('new_words: ' + ', '.join(new_words) + '\n')
        out.write('known_words: ' + ', '.join(known_words) + '\n')

if __name__ == '__main__':
    main()
