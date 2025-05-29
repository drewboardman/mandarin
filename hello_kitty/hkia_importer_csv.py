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

    # Load SUBTLEX chars and words
    subtlex_chars = set()
    subtlex_words = set()
    try:
        cur = conn.execute('SELECT character FROM subtlex_chars')
        for (char,) in cur.fetchall():
            subtlex_chars.add(char)
    except Exception:
        pass
    try:
        cur = conn.execute('SELECT word FROM subtlex_words')
        for (word,) in cur.fetchall():
            subtlex_words.add(word)
    except Exception:
        pass

    # Parse CEDICT
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
                    cleaned = re.split(r'[;(\[]', translations[0])[0].strip()
                    dictionary[simp] = (cleaned, pinyin)
        return dictionary

    cedict_path = '../cedict_ts.u8'
    cedict_dict = parse_cedict(cedict_path)

    # Ensure suspected_words table exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS suspected_words (
            word TEXT PRIMARY KEY,
            valid BOOLEAN,
            added_at DATETIME DEFAULT (datetime('now'))
        )
    ''')

    # Find min/max freq_rank in hkia for random assignment
    cur = conn.cursor()
    cur.execute(f"SELECT MIN(freq_rank), MAX(freq_rank) FROM {HKIA_TABLE} WHERE freq_rank IS NOT NULL")
    min_freq, max_freq = cur.fetchone()
    if min_freq is None or max_freq is None:
        min_freq, max_freq = 1, 1000000  # fallback if table is empty
    freq_range = max_freq - min_freq
    lower_bound = int(min_freq + 0.5 * freq_range)

    known_found = set()
    not_found_in_freq_set = set()
    not_found_anywhere_set = set()
    found_in_cedict_set = set()
    with open(INPUT_CSV, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Join all columns to reconstruct the full sentence
            phrase = ''.join(row).strip()
            if not phrase:
                continue
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
                in_subtlex_word = word in subtlex_words
                in_subtlex_char = word in subtlex_chars
                in_char_names = word in char_names
                if (freq_rank is None) and (not in_subtlex_word) and (not in_subtlex_char) and (not in_char_names):
                    not_found_anywhere_set.add(word)
                    if word in cedict_dict:
                        found_in_cedict_set.add(word)
                        rand_freq = random.randint(lower_bound, max_freq)
                        upsert_word(conn, word, rand_freq)
                    else:
                        # Insert into suspected_words instead of hkia
                        conn.execute('INSERT OR IGNORE INTO suspected_words (word, valid) VALUES (?, NULL)', (word,))
                elif (freq_rank is not None):
                    upsert_word(conn, word, freq_rank)
                else:
                    # If freq_rank is None but found in SUBTLEX or char_names, insert into suspected_words
                    conn.execute('INSERT OR IGNORE INTO suspected_words (word, valid) VALUES (?, NULL)', (word,))

    conn.commit()
    total_words = count_words(conn, HKIA_TABLE)
    total_known_found = len(known_found)

    # Find freq_rank range (for info only, not for assignment)
    cur = conn.cursor()
    cur.execute(f"SELECT MIN(freq_rank), MAX(freq_rank) FROM {HKIA_TABLE} WHERE freq_rank IS NOT NULL")
    min_freq, max_freq = cur.fetchone()
    cur.execute(f"SELECT COUNT(*) FROM {HKIA_TABLE} WHERE freq_rank IS NULL")
    null_count = cur.fetchone()[0]

    print(f"Import complete. {total_words} unique words in the hkia table.")
    print(f"{total_known_found} words from this session were already found in the known_words table and skipped.")
    print(f"{len(found_in_cedict_set)} words not found in any frequency table but found in CEDICT were added to hkia with a random freq_rank.")
    print(f"{len(not_found_anywhere_set) - len(found_in_cedict_set)} words not found in any frequency table or CEDICT were added to suspected_words.")
    print(f"min_freq: {min_freq}, max_freq: {max_freq}, null_count: {null_count}")

    conn.close()

if __name__ == "__main__":
    main()