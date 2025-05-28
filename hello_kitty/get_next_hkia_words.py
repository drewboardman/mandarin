import sqlite3
import re

DB_FILE = '../freq_words.db'
OUTPUT_FILE_LINES = 'next_hkia_words.txt'
OUTPUT_FILE_CSV = 'next_hkia_words_comma.txt'
DEFAULT_N = 150
HKIA_TABLE = 'hkia'
KNOWN_WORDS_TABLE = 'known_words'

def is_chinese(word):
    return bool(re.fullmatch(r'[\u4e00-\u9fff]+', word))

def main():
    n = DEFAULT_N
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(f'''
    SELECT h.freq_rank, h.word
    FROM {HKIA_TABLE} h
    LEFT JOIN {KNOWN_WORDS_TABLE} k ON h.word = k.word
    WHERE h.freq_rank IS NOT NULL
    ORDER BY h.freq_rank DESC
    ''')

    count = 0
    results = []
    words_only = []
    found_in_known = 0
    for freq_rank, word in cur.fetchall():
        if is_chinese(word):
            # Double check not in known_words
            cur2 = conn.execute(f'SELECT 1 FROM {KNOWN_WORDS_TABLE} WHERE word=?', (word,))
            if cur2.fetchone():
                found_in_known += 1
                continue
            results.append((freq_rank, word))
            words_only.append(word)
            count += 1
            if count >= n:
                break

    conn.close()

    # Write results as word, one per line (no freq_rank)
    with open(OUTPUT_FILE_LINES, 'w', encoding='utf-8') as f:
        for word in words_only:
            f.write(f"{word}\n")

    # Write results as comma+space separated, only the word
    with open(OUTPUT_FILE_CSV, 'w', encoding='utf-8') as f:
        f.write(', '.join(words_only) + '\n')

    print(f"Saved {count} HKIA words to {OUTPUT_FILE_LINES} and {OUTPUT_FILE_CSV}")
    print(f"{found_in_known} words were found in known_words and skipped (should be zero)")

if __name__ == "__main__":
    main()
