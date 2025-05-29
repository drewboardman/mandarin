import jieba

# Test words
words = ["中国", "的", "测试", "不存在的词"]

for word in words:
    freq = jieba.suggest_freq(word, True)
    print(f"Word: {word}, jieba.suggest_freq: {freq}")

# Try to access the internal frequency dict
try:
    freq_dict = jieba.dt.FREQ
    for word in words:
        print(f"Word: {word}, jieba internal freq: {freq_dict.get(word)}")
except Exception as e:
    print(f"Error accessing jieba internal frequency dict: {e}")
