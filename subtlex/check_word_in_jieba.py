import jieba

word = "我时"

if word in jieba.dt.FREQ:
    print(f'"{word}" is in jieba\'s dictionary.')
else:
    print(f'"{word}" is NOT in jieba\'s dictionary.')

# Additionally, see how jieba segments your sentence:
sentence = "不过我得提醒你,下次你看到我时,我可能就在跳舞了"
print("Segmented sentence:", list(jieba.cut(sentence)))