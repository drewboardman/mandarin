I have a list of Chinese words in a file, one word per line. For each word, generate a tab-separated row with the following columns (in order). Go through each row in the file and replace it with the following:

Chinese word

English meaning

Pinyin for the word

Example sentence in Chinese (using the target word)

English translation of the example sentence

Pinyin for the example sentence

✅ Requirements for the example sentence:
Must be simple and beginner-appropriate, using high-frequency vocabulary when possible.

Must provide clear context so the meaning of the word can be inferred naturally.

Avoid sentences with no context or only direct translations (e.g., “我爱你” is a bad example).

Prefer sentences with light descriptive or situational detail (e.g., “下午我有点儿累，想打个盹” is a good example for “打盹”).

🔎 Additional Preprocessing Instructions:
Before generating output, scan and filter the input word list. Remove:

❌ Malformed, broken, or nonsensical words, such as:

Data-join artifacts: e.g., “要和史”, “中会”, “史中”

Partial function words or stray particles: e.g., “不多”, “这人”, “太会”

Character combinations that do not appear in major corpora (CC-CEDICT, SUBTLEX-CH, HSK lists, etc.), and are not idioms, fixed expressions, or personal names.

❌ Trivial or overly generic constructions with no standalone educational value, including:

Simple negated fragments: “不来”, “不信”, “不熟”

Redundant demonstrative + noun pairings: “这事”, “这身”

Context-free partial auxiliaries or modifiers: “太会”, “可要”, “已”, “之事”

✅ However, do keep low-frequency but legitimate expressions that:

Have meaning in context (e.g., “卡在”, “包在”)

Are valid compound verbs, nouns, or set phrases

📄 Output Format (tab-separated):
Chinese_word[TAB]English_meaning[TAB]Pinyin[TAB]Example_sentence_CN[TAB]Example_sentence_EN[TAB]Example_sentence_Pinyin
Example:
行	walk	xíng	我每天走路去学校。	I walk to school every day.	wǒ měi tiān zǒu lù qù xué xiào 。

⚠️ Final Report:
At the end of the output, report how many entries were removed due to being malformed, trivial, or invalid:

⚠️ Removed [X] invalid word(s) from the input due to being malformed, trivial, or non-existent in Mandarin.