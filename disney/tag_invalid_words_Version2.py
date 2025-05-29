import sqlite3

# List of "nonsense" or invalid words/phrases found by LLM
invalid_words = [
    "中船","中派","中高","之事","之人","之门","会卡","会弹","会教","回人",
    "土里","大猫","大点","大眼","太会","太美","太少","太长","失到","当个","当起",
    "所选","所写","我想","打到","打来","推到","掉到","找起","拍成","拍得","提过",
    "推到","掉到","掉进","撞到","抓到","接来","提过","搜到","放好","放上","摆成",
    "摆个","挂到","挂起","推到","掉到","撞到","挂到","搜到","放上","摆成","摆个",
    "挂到","挂起","搬到","撞上","撞到","搬到","摔到","摔下","提到","提起","接到",
    "找来","救到","救起","教到","教起","教来","推到","掉到","掉下","掉进","抓到",
    "接到","敲到","敲起","掉到","掉进","掉下","抓到","撞到","撞上","撞下","撞进"
]

DB_PATH = '../freq_words.db'  # Adjust path if needed

def tag_invalid_words(db_path, invalid_words):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    updated = 0
    for word in set(invalid_words):  # Remove duplicates
        cur.execute(
            "UPDATE suspected_words SET valid=0 WHERE word=? AND tag='disney'",
            (word,)
        )
        if cur.rowcount > 0:
            updated += 1
    conn.commit()
    print(f"Marked {updated} words as invalid in the suspected_words table with tag 'disney'.")
    conn.close()

if __name__ == '__main__':
    tag_invalid_words(DB_PATH, invalid_words)