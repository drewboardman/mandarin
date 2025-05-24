# Chinese Frequency Vocabulary Toolkit

This directory helps you build your own Chinese vocabulary learning database and generate frequency-based word lists for language study and Anki import.

---

## 📥 1. Download the BCC Chinese Frequency List

You will need the BCC corpus frequency list, which is available from Pleco Forums:
- [Word frequency list based on a 15 billion character corpus (BCC/BLCU Chinese Corpus)](https://www.plecoforums.com/threads/word-frequency-list-based-on-a-15-billion-character-corpus-bcc-blcu-chinese-corpus.5859/)

**Download the file (usually called `BCC-Finalresult.txt` or similar) and place it in this directory.**

---

## 🗄️ 2. Build the Database

Create a SQLite database (`freq_words.db`) and import the frequency list.

**a. Create the tables:**

```sql
-- In your SQLite client (e.g., sqlite3 freq_words.db)
CREATE TABLE freq_words (
    rank INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    frequency INTEGER NOT NULL
);

CREATE TABLE known_words (
    word TEXT PRIMARY KEY
);
```

**b. Import the frequency list:**

Assuming the downloaded file is tab-separated and has columns: rank, word, frequency:

```bash
sqlite3 freq_words.db
.mode tabs
.import BCC-Finalresult.txt freq_words
.exit
```
*(If your file format is different, adjust accordingly.)*

---

## ✅ 3. Mark Known Words

Add words you've already learned to the `known_words` table.  
You can do this manually, or by importing from your Anki export or another source.

**Example SQL:**
```sql
INSERT INTO known_words (word) VALUES ('的');
```
Or, if you have a text file with one known word per line:
```bash
sqlite3 freq_words.db
.mode list
.import known_words.txt known_words
```

---

## 🐍 4. Run Scripts

### a. Generate Unknown Words Lists

Use the provided script to generate the next N unknown, high-frequency Chinese words.

```bash
python get_next_unknown_words.py [number_of_words]
```
- Default: 250 words if you don't specify a number.
- Outputs:
  - `next_unknown_words.txt` with lines like: `178	重要`
  - `next_unknown_words_comma.txt` with a single comma+space-delimited line: `重要, 世界, ...`

### b. (Optional) Anki Export

You can adapt or extend the scripts to create CSVs for Anki import, or use the output words to create your own flashcards.

---

## 📝 File Reference

- `get_next_unknown_words.py`: Main script for generating unknown word lists.
- `freq_words.db`: SQLite database with frequency and known words tables.
- `next_unknown_words.txt`: Tab-separated rank and word output.
- `next_unknown_words_comma.txt`: Comma+space separated word list.
- *(Add your known words file as `known_words.txt` if importing.)*

---

## 🚀 Example Workflow

1. Download and place the BCC file in this directory.
2. Create the database and tables (step 2 above).
3. Add your known words to the database.
4. Run `python get_next_unknown_words.py 250` to get your next 250 high-frequency unknown words.
5. Use the output files to guide your studies or generate Anki cards.

---

## 📚 Source

**Frequency data courtesy of:**  
[Pleco Forums: BCC 15 Billion Character Frequency List](https://www.plecoforums.com/threads/word-frequency-list-based-on-a-15-billion-character-corpus-bcc-blcu-chinese-corpus.5859/)

---

Happy studying!