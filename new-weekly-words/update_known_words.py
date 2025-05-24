import sqlite3

DB_FILE = 'freq_words.db'
KNOWN_FILE = 'known_words.txt'

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create the known_words table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS known_words (
        word TEXT PRIMARY KEY
    )
""")

# Insert words from the known_words.txt file
with open(KNOWN_FILE, encoding="utf-8") as f:
    for line in f:
        word = line.strip()
        if word:
            try:
                cur.execute("INSERT OR IGNORE INTO known_words (word) VALUES (?)", (word,))
            except Exception as e:
                print(f"Error inserting {word}: {e}")

conn.commit()
conn.close()