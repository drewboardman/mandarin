This directory will help you take your anki known words and find the next `n` words to learn. The idea is that you're going to put these into an AI and prompt it to make you a "graded reader". This reader will:

 * contain all `n` of the new words in the story
 * any of the "legacy" words you already know
 * ideally nothing more outside of character names or places

The basic idea is we're going to continually get the most efficient new words to learn, make an anki deck with them, then read the graded reader. This is intended to structure your learning in the smartest way possible.

I'm using sql here because these word lists are enormous, and I don't want to worry about performance or anything silly.

## VENV
Go into the `new-weekly-words/` dir and start a venv:

```
cd mandarin/new-weekly-words
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Get the word frequency list
You need to download the word frequency codex thing. Here is where I got it:

https://www.plecoforums.com/threads/word-frequency-list-based-on-a-15-billion-character-corpus-bcc-blcu-chinese-corpus.5859/

It's the `global_wordfreq.release_UTF-8.txt` that I used.

## Create the db
In your venv, run the script:

```
python setup_frequency_db.py
```

This should create a database and table for this big file you downloaded.

## Get your known cards from anki
In anki:

 * Browse 
 * select "Review" on the left 
 * select/highlight all these cards
 * at the top select "Notes"
 * "Export Notes"
 * Export Format: Notes in plain text
 * unselect all options

save this as "raw_notes.txt" in this `new-weekly-words` directory.

NOTE: My words spanned a few different formats, and the script accounts for that. For example:

```
330	地方	地方	dìfang	place; space; room; part, (fāng: local; regional)	noun		这个城市是我出生的地方。	這個城市是我出生的地方。	Zhège chéngshì shì wǒ chūshēng de dìfang.	This city is where I was born.				
了	already, finished	le	他已经吃了饭。	He has already eaten.		
```

these two lines are slightly different, and I want the word only.

## Extract the words from the raw Anki
Run the script:

```
python extract_mandarin_words.py
```

This will simply create a big file with all your words in it, 1 per row. **Do not** worry about dupes here, the next step will handle that smoothly every single time.

## Add these known words to the known words sql table

This will take all of your words and put them into another SQLite table. Each time you do this with your new words, the script will automatically update everything for you. It takes into account duplicates, so don't worry about that:

```
python update_known_words.py
```

## Get the next best words (our actual goal)
Now for the moment of truth. This script is going to grab the next `n` words that are statistically most frequently used amongst all content. It defaults to 250, but change it to however much you think you can handle.

```
python get_next_known_words.py
```

or, alternatively

```
python get_next_known_words.py 350
```

whatever number you want.

This creates two files:

  1. `next_unknown_words.txt`
  2. `next_unknown_words_comma.txt`

## Next steps
Ok so the whole purpose of this is two things:

  1. You're going to take these new words and create an Anki deck with them. See the `anki_decks/` directory and README.md for instructions on how to do that.
  2. You're going to prompt the AI of your choice to generate a graded reader for you that uses these words and the legacy words. I'm currently working on a structured way to achieve this and will update the repository with that module.