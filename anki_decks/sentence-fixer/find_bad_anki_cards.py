# This script scans an exported Anki deck (plain text, tab-separated) and outputs a list of words
# that have either:
#   1. A definition containing the word "variant"
#   2. An example sentence with fewer than 6 Chinese characters (ignoring punctuation and spaces)
# The output is a file with one word per row.

import sys
import re

def is_chinese_char(char):
    """Returns True if char is a Chinese character."""
    return '\u4e00' <= char <= '\u9fff'

def count_chinese_chars(s):
    """Counts the number of Chinese characters in a string."""
    return sum(1 for char in s if is_chinese_char(char))

def find_bad_cards(input_filename, output_filename):
    bad_words = set()
    with open(input_filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or meta lines
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            if len(fields) < 4:
                continue  # Not enough fields for a valid card
            word = fields[0].strip()
            definition = fields[1].strip().lower()
            example_cn = fields[3].strip()
            # 1. Check for "variant" in the definition
            if "variant" in definition:
                bad_words.add(word)
                continue
            # 2. Check for short Chinese example sentences (<6 chars)
            if count_chinese_chars(example_cn) < 5:
                bad_words.add(word)
                continue
    # Write output
    with open(output_filename, 'w', encoding='utf-8') as out:
        for word in sorted(bad_words):
            out.write(f"{word}\n")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python find_bad_anki_cards.py input.txt output.txt")
        sys.exit(1)
    find_bad_cards(sys.argv[1], sys.argv[2])