import sqlite3
import os

FREQ_FILE = 'global_wordfreq.release_UTF-8.txt'  # Your wordlist: word<TAB>frequency
DB_FILE = 'freq_words.db'

def setup_db():
    # Connect (creates file if not exists)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS freq_words (
            word TEXT PRIMARY KEY,
            frequency INTEGER,
            rank INTEGER
        )
    """)
    # Index for faster queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rank ON freq_words(rank)")
    # Only populate if empty
    cur.execute("SELECT COUNT(*) FROM freq_words")
    if cur.fetchone()[0] == 0:
        print("Populating database from frequency list...")
        with open(FREQ_FILE, encoding='utf-8') as f:
            for i, line in enumerate(f, 1):  # 1-based rank
                parts = line.strip().split('\t')
                if len(parts) != 2: continue
                word, freq = parts
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO freq_words (word, frequency, rank) VALUES (?, ?, ?)",
                        (word, int(freq), i)
                    )
                except Exception as e:
                    print(f"Error inserting word '{word}': {e}")
        conn.commit()
        print("Database populated.")
    else:
        print("Database already populated.")
    conn.close()

if __name__ == '__main__':
    setup_db()