import sqlite3
import csv

REFOLD_FILE = 'new-weekly-words/refold_review.txt'
MASTER_FILE = 'new-weekly-words/master.txt'
OUTPUT_FILE = 'new-weekly-words/refold_not_in_master.txt'

def extract_words(filepath, word_col, skip_lines=2):
    words = set()
    with open(filepath, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for _ in range(skip_lines):
            next(reader, None)
        for row in reader:
            if len(row) > word_col:
                word = row[word_col].strip()
                if word:
                    words.add(word)
    return words

def main():
    # Extract words
    refold_words = extract_words(REFOLD_FILE, 1)
    master_words = extract_words(MASTER_FILE, 0)

    # Use SQLite in-memory DB
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE refold (word TEXT PRIMARY KEY)')
    c.execute('CREATE TABLE master (word TEXT PRIMARY KEY)')

    c.executemany('INSERT INTO refold (word) VALUES (?)', [(w,) for w in refold_words])
    c.executemany('INSERT INTO master (word) VALUES (?)', [(w,) for w in master_words])

    # Diff: words in refold not in master
    c.execute('''
        SELECT word FROM refold
        WHERE word NOT IN (SELECT word FROM master)
        ORDER BY word
    ''')
    diff_words = [row[0] for row in c.fetchall()]

    # Output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for word in diff_words:
            f.write(word + '\n')
    print(f"Wrote {len(diff_words)} words to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
