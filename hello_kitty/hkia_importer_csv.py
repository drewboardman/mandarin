import sqlite3
import jieba
import csv
import re
import random

WORD_FREQ_DB = "../freq_words.db"
WORD_FREQ_TABLE = "freq_words"
KNOWN_WORDS_TABLE = "known_words"
HKIA_TABLE = "hkia"
CHAR_NAME_PATH = "character_names.txt"
INPUT_CSV = "input.csv"

def contains_chinese(s):
    return re.search(r'[\u4e00-\u9fff]', s) is not None

def load_word_freq_from_db(conn, table):
    freq = {}
    cursor = conn.execute(f"SELECT word, rank FROM {table}")
    for word, rank in cursor.fetchall():
        freq[word] = rank
    return freq

def load_known_words(conn, table):
    known = set()
    try:
        cursor = conn.execute(f"SELECT word FROM {table}")
        for (word,) in cursor.fetchall():
            known.add(word)
    except sqlite3.OperationalError:
        pass  # Table might not exist
    return known

def load_character_names(path):
    names = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 1:
                    chinese = parts[0]
                    english = parts[1] if len(parts) > 1 else ""
                    names[chinese] = english
                    jieba.add_word(chinese)
    except FileNotFoundError:
        pass
    return names

def setup_hkia_table(conn):
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {HKIA_TABLE} (
        word TEXT PRIMARY KEY,
        freq_rank INTEGER,
        updated_at DATETIME DEFAULT (datetime('now'))
    );
    """)

def upsert_word(conn, word, freq_rank):
    conn.execute(
        f"INSERT INTO {HKIA_TABLE} (word, freq_rank, updated_at) VALUES (?, ?, datetime('now')) "
        f"ON CONFLICT(word) DO UPDATE SET freq_rank=excluded.freq_rank, updated_at=datetime('now')",
        (word, freq_rank)
    )

def count_words(conn, table):
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

def main():
    conn = sqlite3.connect(WORD_FREQ_DB)
    setup_hkia_table(conn)
    word_freq = load_word_freq_from_db(conn, WORD_FREQ_TABLE)
    known_words = load_known_words(conn, KNOWN_WORDS_TABLE)
    char_names = load_character_names(CHAR_NAME_PATH)

    known_found = set()

    with open(INPUT_CSV, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or not row[0].strip():
                continue
            phrase = row[0].strip()
            if not contains_chinese(phrase) and phrase not in char_names:
                continue
            for word in jieba.cut(phrase):
                word = word.strip()
                if not word or word in ('……', '...', '《', '》', '!', '！'):
                    continue
                if not contains_chinese(word) and word not in char_names:
                    continue
                if word in known_words:
                    known_found.add(word)
                    continue  # Skip if already known
                freq_rank = word_freq.get(word)
                upsert_word(conn, word, freq_rank)

    conn.commit()
    total_words = count_words(conn, HKIA_TABLE)
    total_known_found = len(known_found)

    # Find freq_rank range
    cur = conn.cursor()
    cur.execute(f"SELECT MIN(freq_rank), MAX(freq_rank) FROM {HKIA_TABLE} WHERE freq_rank IS NOT NULL")
    min_freq, max_freq = cur.fetchone()
    cur.execute(f"SELECT COUNT(*) FROM {HKIA_TABLE} WHERE freq_rank IS NULL")
    null_count = cur.fetchone()[0]

    assigned = 0
    if min_freq is not None and max_freq is not None and null_count > 0:
        # Top 40% means: assign between lower_bound (60% of range) and max_freq
        freq_range = max_freq - min_freq
        lower_bound = int(min_freq + 0.6 * freq_range)
        cur.execute(f"SELECT word FROM {HKIA_TABLE} WHERE freq_rank IS NULL")
        null_words = [row[0] for row in cur.fetchall()]
        for word in null_words:
            rand_freq = random.randint(lower_bound, max_freq)
            conn.execute(f"UPDATE {HKIA_TABLE} SET freq_rank=? WHERE word=?", (rand_freq, word))
            assigned += 1
        conn.commit()
        # Recompute min/max after assignment
        cur.execute(f"SELECT MIN(freq_rank), MAX(freq_rank) FROM {HKIA_TABLE}")
        new_min, new_max = cur.fetchone()
        print(f"\n{assigned} words with missing freq_rank were assigned random values in the top 40% (most frequent) of the frequency range.")
        print(f"Assignment range: {lower_bound} (60% of range) to {max_freq} (most frequent). New min: {new_min}, new max: {new_max}.")
    else:
        print(f"\nNo freq_rank assignment needed or possible. min_freq: {min_freq}, max_freq: {max_freq}, null_count: {null_count}")

    print(f"Import complete. {total_words} unique words in the hkia table.")
    print(f"{total_known_found} words from this session were already found in the known_words table and skipped.")

    conn.close()

if __name__ == "__main__":
    main()