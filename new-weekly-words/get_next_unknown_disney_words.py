import sqlite3
import re
import sys

DB_FILE = '../freq_words.db'  # Change to disney.db if needed
OUTPUT_FILE_LINES = 'next_unknown_disney_words.txt'
OUTPUT_FILE_CSV = 'next_unknown_disney_words_comma.txt'
DEFAULT_N = 250

def is_chinese(word):
    return bool(re.fullmatch(r'[\u4e00-\u9fff]+', word))

def main():
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    except ValueError:
        print("Usage: python get_next_unknown_disney_words.py [number_of_words]")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    SELECT d.frequency, d.word
    FROM disney d
    LEFT JOIN known_words kw ON d.word = kw.word
    WHERE kw.word IS NULL
    ORDER BY d.frequency DESC
    """)

    count = 0
    results = []
    words_only = []
    for frequency, word in cur.fetchall():
        if is_chinese(word):
            results.append((frequency, word))
            words_only.append(word)
            count += 1
            if count >= n:
                break

    conn.close()

    # Write results as word, one per line
    with open(OUTPUT_FILE_LINES, 'w', encoding='utf-8') as f:
        for _, word in results:
            f.write(f"{word}\n")

    # Write results as comma+space separated, only the word
    with open(OUTPUT_FILE_CSV, 'w', encoding='utf-8') as f:
        f.write(', '.join(words_only) + '\n')

    print(f"Saved {count} unknown Chinese words to {OUTPUT_FILE_LINES} and {OUTPUT_FILE_CSV}")

if __name__ == "__main__":
    main()
