import sqlite3
import csv
import os
import sys

DB_FILE = 'freq_words.db'


def get_words_from_csv(csv_path):
    words = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for word in row:
                word = word.strip()
                if word:
                    words.add(word)
    return words


def main():
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        print("Usage: python count_unknown_words_in_csv.py <csv_file>")
        return
    csv_path = os.path.join(os.path.dirname(__file__), csv_file)
    db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
    words = get_words_from_csv(csv_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create a temporary table for CSV words
    cur.execute('CREATE TEMPORARY TABLE temp_csv_words (word TEXT PRIMARY KEY)')
    cur.executemany('INSERT INTO temp_csv_words (word) VALUES (?)', [(w,) for w in words])

    # Count unknown words
    cur.execute('''
        SELECT COUNT(*) FROM temp_csv_words tcw
        LEFT JOIN known_words kw ON tcw.word = kw.word
        WHERE kw.word IS NULL
    ''')
    unknown_count = cur.fetchone()[0]

    # Optionally, get a sample of unknown words
    cur.execute('''
        SELECT tcw.word FROM temp_csv_words tcw
        LEFT JOIN known_words kw ON tcw.word = kw.word
        WHERE kw.word IS NULL
    ''')
    all_unknown = [row[0] for row in cur.fetchall()]

    # Write all unknown words to file
    output_path = os.path.join(os.path.dirname(__file__), 'words_for_ai.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in all_unknown:
            f.write(word + '\n')

    print(f"Total words in CSV: {len(words)}")
    print(f"Number of unknown words: {unknown_count}")
    print(f"Sample unknown words: {all_unknown[:20]}")
    print(f"All unknown words written to {output_path}")

    conn.close()


if __name__ == "__main__":
    main()
