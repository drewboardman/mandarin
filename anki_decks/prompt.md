Prompt for AI Flashcard Generation

I have a list of Chinese words in a file, one word per line. For each word, generate a tab-separated row with the following columns (in order):

Chinese word
English meaning
Pinyin for word
Example sentence in Chinese (using the target word)
English translation of the example sentence
Pinyin for the example sentence

Requirements for the example sentence:

The sentence must be simple and appropriate for a beginner, using high-frequency vocabulary when possible.
The sentence must provide clear context so that the meaning of the target word can be inferred from the context.
Avoid sentences with no context or with only direct translations (e.g., “我爱你” is a bad example).
Prefer sentences that use the word in a situation or with descriptive details (e.g., “下午我有点儿累，想打个盹” is a good example for “打盹”).

Output format (tab-separated):

Chinese_word [tab] English_meaning [tab] Pinyin [tab] Example_sentence_CN [tab] Example_sentence_EN [tab] Example_sentence_Pinyin

Example:

行 walk xíng 我每天走路去学校。 I walk to school every day. wǒ měi tiān zǒu lù qù xué xiào 。