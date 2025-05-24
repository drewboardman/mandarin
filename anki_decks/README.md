# Mandarin Anki Deck Generator

This tool helps you create Anki flashcards for Mandarin Chinese vocabulary using a CC-CEDICT dictionary for definitions and pinyin. It supports a simple tab-separated input format and outputs a tab-separated file ready for Anki import.

---

## 1. Virtual Environment (venv) Setup

It's best to use a Python virtual environment to manage dependencies.

### Create and Activate venv

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# On Windows (cmd)
venv\Scripts\activate

# On Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### Install Dependencies

Only `pypinyin` is required:

```bash
pip install pypinyin
```

---

## 2. CC-CEDICT Setup

The script uses the [CC-CEDICT dictionary](https://www.mdbg.net/chinese/dictionary?page=cc-cedict) for Mandarin definitions.

- Download the latest `cedict_ts.u8` from [here](https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz).
- Unzip the file and rename it to `cedict_ts.u8` if needed.
- Place `cedict_ts.u8` in the same directory as the script or specify its path using `--cedict`.

---

## 3. Preparing Your Input File

> **Note:**  
> I **highly** recommend you check out the `new-weekly-words/` module in this repository. This will organize how you generate each deck you want to create. The general idea is that each deck will be the next `n` statistically most frequently used words across all Chinese media content.

Prepare a UTF-8 encoded, tab-separated file (e.g., `anki_decks/sample_deck.txt`) in the format:

```
WORD    CHINESE_SENTENCE    ENGLISH_TRANSLATION
```

**Example:**
```
你的	你的手机在哪儿？	Where is your phone?
朋友	朋友来了。	My friend came.
喜欢	我喜欢学习中文。	I like studying Chinese.
```

- Each line: one word, one sample sentence in Chinese, one sample sentence in English, separated by tabs.
- No header row required.

**To prompt AI (like Copilot or ChatGPT) to generate this:**
> Give me a tab-separated list of Mandarin words, each with a sample sentence in Chinese using the word, and the English translation. Example format:  
> 你的	你的手机在哪儿？	Where is your phone?

---

## 4. Running the Script

With your venv active and the cedict file in place, run:

```bash
python anki_decks/process_human_input_deck.py --input-file=anki_decks/sample_deck.txt --output-file=anki_decks/sample_deck_out.txt
```

- By default, the script looks for `cedict_ts.u8` in the current directory.
- To specify a different dictionary path, use `--cedict`:

```bash
python anki_decks/process_human_input_deck.py --input-file=anki_decks/sample_deck.txt --output-file=anki_decks/sample_deck_out.txt --cedict=/path/to/cedict_ts.u8
```

---

## 5. Output

The script writes a tab-separated file (default: `anki_decks/sample_deck_out.txt`) with these columns:

| Word | Meaning | Pinyin | Chinese Sentence (with bolded word) | English Sentence | Sentence Pinyin |
|------|---------|--------|-------------------------------------|------------------|----------------|

- In the Chinese sentence column, the target word will be bolded using HTML, e.g.:  
  `<b>你的</b>手机在哪儿？`

You can import this file directly into Anki.

---

## Notes

- The script always uses the **first CC-CEDICT definition** for a word, even if it is a "variant of" or "old variant" meaning. This matches the dictionary order and frequency.
- If the word is not found, it will fall back to character-by-character definitions, joined by a semicolon.
- You can manually edit the meaning column in Anki after import if you want to refine or override definitions.

---

## License

This project uses the CC-CEDICT dictionary, which is licensed under the [Creative Commons Attribution-Share Alike 3.0 License](https://creativecommons.org/licenses/by-sa/3.0/).