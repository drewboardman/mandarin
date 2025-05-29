import os
import sqlite3
import jieba
import re
from tqdm import tqdm
import argparse
import random

DB_PATH = os.path.abspath(os.path.join('..', 'freq_words.db'))
ROOT_DIR = 'LocDB_zh-CN'

def extract_chinese_from_file(path):
    results = []
    with open(path, 'rb') as f:
        data = f.read()
    i = 0
    while i < len(data):
        sep = data.find(b'\x12', i)
        if sep == -1:
            break
        if sep + 2 > len(data):
            break
        length = data[sep+1]
        value_bytes = data[sep+2:sep+2+length]
        try:
            value = value_bytes.decode('utf-8')
        except UnicodeDecodeError:
            i = sep + 2 + length
            continue
        if re.search(r'[\u4e00-\u9fff]', value):
            results.append(value)
        i = sep + 2 + length
    return results

def segment_phrases(phrases):
    segmented = []
    for phrase in tqdm(phrases, desc="Segmenting phrases"):
        for word in jieba.cut(phrase, cut_all=False):
            word = word.strip()
            if word and re.search(r'[\u4e00-\u9fff]', word):
                segmented.append(word)
    return segmented

def main():
    parser = argparse.ArgumentParser(description="Process Disney .locbin files and update vocabulary tables.")
    parser.add_argument('--tag', type=str, default='disney', help='Tag to use for suspected_words entries (default: disney)')
    args = parser.parse_args()
    tag = args.tag

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Create disney table if not exists
    cur.execute('CREATE TABLE IF NOT EXISTS disney (word TEXT PRIMARY KEY, freq_rank INTEGER)')
    # Do NOT create suspected_words or known_words, just use them
    # Ensure suspected_words has a tag column
    cur.execute("PRAGMA table_info(suspected_words)")
    columns = [row[1] for row in cur.fetchall()]
    if 'tag' not in columns:
        cur.execute('ALTER TABLE suspected_words ADD COLUMN tag TEXT')
    # Query known_words
    cur.execute('SELECT word FROM known_words')
    known_words = {row[0] for row in cur.fetchall()}

    # Collect all .locbin files
    file_list = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for fname in files:
            if fname.endswith('.locbin'):
                file_list.append(os.path.join(root, fname))

    all_phrases = []
    for path in tqdm(file_list, desc="Extracting Chinese from files"):
        all_phrases.extend(extract_chinese_from_file(path))

    # Segment words
    segmented = segment_phrases(all_phrases)

    processed_words = set()
    added_disney = 0
    already_known = 0
    added_suspect = 0
    cedict_only_count = 0
    jieba_only_count = 0

    # Parse CEDICT and assign a pseudo-frequency for top 40% most frequent words
    def parse_cedict_with_freq(path):
        dictionary = {}
        lines = []
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                match = re.match(r"(\S+)\s+(\S+)\s+\[(.+?)\]\s+/(.+)/", line)
                if match:
                    trad, simp, pinyin, eng = match.groups()
                    translations = eng.split('/')
                    cleaned = re.split(r'[;(\[]', translations[0])[0].strip()
                    lines.append((simp, cleaned, pinyin))
        # Assign pseudo-frequency: top 40% get a rank, rest are None
        total = len(lines)
        cutoff = int(total * 0.4)
        for i, (simp, cleaned, pinyin) in enumerate(lines):
            freq_rank = i + 1 if i < cutoff else None
            dictionary[simp] = (cleaned, pinyin, freq_rank)
        return dictionary

    cedict_path = os.path.abspath(os.path.join('..', 'cedict_ts.u8'))
    cedict_dict = parse_cedict_with_freq(cedict_path)

    # Before processing, get min/max freq_rank in disney table (for top 40% assignment)
    cur.execute('SELECT MIN(freq_rank), MAX(freq_rank) FROM disney WHERE freq_rank IS NOT NULL')
    min_freq, max_freq = cur.fetchone()
    if min_freq is None or max_freq is None:
        # If no freq values yet, set defaults
        min_freq, max_freq = 1, 1000
    freq_range = max_freq - min_freq
    top_40_cutoff = min_freq + int(freq_range * 0.4)

    for word in tqdm(segmented, desc="Processing segmented words"):
        if word in processed_words:
            continue
        processed_words.add(word)
        if word in known_words:
            already_known += 1
            continue
        # Check freq_words
        cur.execute('SELECT rank FROM freq_words WHERE word = ?', (word,))
        row = cur.fetchone()
        if row:
            cur.execute('INSERT OR IGNORE INTO disney (word, freq_rank) VALUES (?, ?)', (word, row[0]))
            added_disney += 1
            continue
        # Check subtlex_words
        cur.execute('SELECT freq_count FROM subtlex_words WHERE word = ?', (word,))
        row = cur.fetchone()
        if row:
            cur.execute('INSERT OR IGNORE INTO disney (word, freq_rank) VALUES (?, ?)', (word, None))
            added_disney += 1
            continue
        # Check subtlex_chars
        cur.execute('SELECT freq_count FROM subtlex_chars WHERE character = ?', (word,))
        row = cur.fetchone()
        if row:
            cur.execute('INSERT OR IGNORE INTO disney (word, freq_rank) VALUES (?, ?)', (word, None))
            added_disney += 1
            continue
        # Check CEDICT
        if word in cedict_dict:
            # Assign a random freq_rank in the top 40% of the disney table
            if freq_range > 0:
                freq_rank = random.randint(min_freq, top_40_cutoff)
            else:
                freq_rank = min_freq
            cur.execute('INSERT OR IGNORE INTO disney (word, freq_rank) VALUES (?, ?)', (word, freq_rank))
            added_disney += 1
            cedict_only_count += 1
            continue
        # Check jieba
        if jieba.lcut(word, cut_all=False) == [word]:
            # Assign a random freq_rank in the top 40% of the disney table
            if freq_range > 0:
                freq_rank = random.randint(min_freq, top_40_cutoff)
            else:
                freq_rank = min_freq
            cur.execute('INSERT OR IGNORE INTO disney (word, freq_rank) VALUES (?, ?)', (word, freq_rank))
            added_disney += 1
            jieba_only_count += 1
            continue
        # Not found in any freq table, add or update suspected_words with tag
        cur.execute('SELECT tag FROM suspected_words WHERE word = ?', (word,))
        existing = cur.fetchone()
        if existing:
            if existing[0] != tag:
                cur.execute('UPDATE suspected_words SET tag = ? WHERE word = ?', (tag, word))
        else:
            cur.execute('INSERT INTO suspected_words (word, valid, tag) VALUES (?, NULL, ?)', (word, tag))
        added_suspect += 1

    conn.commit()

    # Count totals
    cur.execute('SELECT COUNT(*) FROM disney')
    disney_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM suspected_words')
    suspect_count = cur.fetchone()[0]
    print(f"Words in disney table: {disney_count}")
    print(f"Words already known: {already_known}")
    print(f"Words added to suspected_words: {added_suspect} (total in table: {suspect_count})")
    print(f"Words added to disney table only from CEDICT: {cedict_only_count}")
    print(f"Words added to disney table only from jieba: {jieba_only_count}")

    conn.close()

if __name__ == '__main__':
    main()