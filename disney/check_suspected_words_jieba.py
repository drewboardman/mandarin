import sqlite3
import jieba

DB_PATH = '../freq_words.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Add found_jieba column if it doesn't exist
    cur.execute("PRAGMA table_info(suspected_words)")
    columns = [row[1] for row in cur.fetchall()]
    if 'found_jieba' not in columns:
        cur.execute('ALTER TABLE suspected_words ADD COLUMN found_jieba INTEGER')
        print("Added 'found_jieba' column to suspected_words table.")
    # Get all words
    cur.execute('SELECT word FROM suspected_words')
    words = [row[0] for row in cur.fetchall()]
    found = 0
    not_found = 0
    for word in words:
        if jieba.lcut(word, cut_all=False) == [word]:
            cur.execute('UPDATE suspected_words SET found_jieba = 1 WHERE word = ?', (word,))
            found += 1
        else:
            cur.execute('UPDATE suspected_words SET found_jieba = 0 WHERE word = ?', (word,))
            not_found += 1
    conn.commit()
    print(f"Words found in jieba: {found}")
    print(f"Words NOT found in jieba: {not_found}")
    conn.close()

if __name__ == '__main__':
    main()
