import sqlite3
import sys

def load_invalid_words(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def flag_invalid_words(db_path, invalid_words, table="suspected_words", word_col="word", valid_col="valid"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    q = f"""
    UPDATE {table}
    SET {valid_col} = 0
    WHERE {word_col} = ?
    """
    for word in invalid_words:
        cur.execute(q, (word,))
        print(f"Flagged '{word}' as invalid.")
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python flag_invalid_words.py path_to_invalid_words.txt")
        sys.exit(1)
    db_path = "../freq_words.db"
    txt_path = sys.argv[1]
    bad_words = load_invalid_words(txt_path)
    flag_invalid_words(db_path, bad_words)