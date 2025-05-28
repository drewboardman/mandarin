import sqlite3
import csv
import os

DB_PATH = '../freq_words.db'
WF_PATH = 'SUBTLEX-CH-WF.txt'
CHR_PATH = 'SUBTLEX-CH-CHR.txt'

def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subtlex_words (
            word TEXT PRIMARY KEY,
            freq_count INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subtlex_chars (
            character TEXT PRIMARY KEY,
            freq_count INTEGER
        )
    ''')

def import_words(conn, filename):
    with open(filename, encoding='gbk') as f:
        next(f)
        next(f)
        reader = csv.DictReader(f, delimiter='\t')
        rows = [
            (row['Word'], int(row['WCount']))
            for row in reader
            if row['Word'] and row['WCount'].isdigit()
        ]
    print(f"Read {len(rows)} word rows from {filename}.")
    conn.executemany(
        'INSERT OR REPLACE INTO subtlex_words (word, freq_count) VALUES (?, ?)',
        rows
    )

def import_chars(conn, filename):
    with open(filename, encoding='gbk') as f:
        next(f)
        next(f)
        reader = csv.DictReader(f, delimiter='\t')
        rows = [
            (row['Character'], int(row['CHRCount']))
            for row in reader
            if row['Character'] and row['CHRCount'].isdigit()
        ]
    print(f"Read {len(rows)} character rows from {filename}.")
    conn.executemany(
        'INSERT OR REPLACE INTO subtlex_chars (character, freq_count) VALUES (?, ?)',
        rows
    )

def main():
    if not os.path.exists(WF_PATH):
        print(f"Missing {WF_PATH}")
        return
    if not os.path.exists(CHR_PATH):
        print(f"Missing {CHR_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    import_words(conn, WF_PATH)
    import_chars(conn, CHR_PATH)
    conn.commit()
    conn.close()
    print("Import complete.")

if __name__ == "__main__":
    main()