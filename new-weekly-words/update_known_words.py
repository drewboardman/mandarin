import sqlite3
import unicodedata

DB_FILE = '../freq_words.db'
KNOWN_FILE = 'known_words.txt'

def extract_word(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    parts = line.split('\t')
    if not parts or not parts[0]:
        return None
    # Skip header lines (if first column is not Chinese or a number)
    if parts[0] == 'word' or parts[0] == '汉字' or parts[0].lower() == 'hanzi':
        return None
    # If first column is a number, word is in second column
    if parts[0].isdigit() and len(parts) > 1:
        word = parts[1]
    else:
        word = parts[0]
    word = word.strip()
    if not word:
        return None
    # Normalize unicode
    word = unicodedata.normalize('NFC', word)
    return word

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create the known_words table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS known_words (
        word TEXT PRIMARY KEY
    )
""")

new_words = 0
with open(KNOWN_FILE, encoding="utf-8") as f:
    for line in f:
        word = extract_word(line)
        if word:
            try:
                cur.execute("INSERT OR IGNORE INTO known_words (word) VALUES (?)", (word,))
                if cur.rowcount == 1:
                    new_words += 1
            except Exception as e:
                print(f"Error inserting {word}: {e}")

conn.commit()
cur.execute("SELECT COUNT(*) FROM known_words")
total_known = cur.fetchone()[0]
print(f"Known words table updated from known_words.txt. {new_words} new words added. Total known words: {total_known}.")
conn.close()