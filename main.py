import pandas as pd
import numpy as np

"""
text を正規化する。
"""
def normalize(text):
    from module.Ocab import Ocab, Regexp
    c = Regexp()
    text1 = c.normalize(text)
    m = Ocab(target=["名詞", "動詞", "形容詞", "副詞"])
    text2 = m.wakati(text1)
    text3 = m.removeStoplist(text2, [])
    return text3


"""
(単語, 品詞)のtupleからなるlistを取得
"""
def word_and_class(text):
    import MeCab
    m = MeCab.Tagger("-Ochasen")
    n_text = normalize(text)
    result = m.parseToNode(n_text)
    word_class = list()
    while result:
        word = result.surface
        class_ = result.feature.split(',')[0]
        if class_ != u'BOS/EOS':
            word_class.append((word, class_))
        result = result.next
    return word_class


"""
textから名詞のみを抽出する
"""
def get_norm(text):
    word_class = word_and_class(text)
    for w_c in word_class.copy():
        if w_c[1] != '名詞':
            word_class.remove(w_c)
    return word_class


"""
2重リストを平滑化する
"""
def flatten(nested_list):
    return [e for inner_list in nested_list for e in inner_list]


"""
問題文から名詞のみを取り出し、リストに追加する。
リストのindexと問題のindexが対応していない（4つずれてる）
"""
def get_bag_of_words(df):
    bag_of_words = list()
    for q in df['問題文']:
        bag_of_words.append(get_norm(q))
    return bag_of_words


"""
どの問題番号の問題文にどの単語が出現したかを0,1で表すdfを取得
"""
def get_vocab_df(df, bag_of_words, all_vocablary):
    vocab_df = pd.DataFrame(index=range(df.shape[0]), columns=all_vocablary, data=0)
    for i, bow in enumerate(bag_of_words):
        for word in bow:
            vocab_df.at[i,word] = 1
    return vocab_df


"""
vocab_df から、同じ単語が2問以上の問題文で使用されているものを取得
形式は(単語, [使用されている問題番号])
"""
def get_duplicated_words(vocab_df):
    duplicated_words = dict()
    for column, value in vocab_df.sum(axis=0).items():
        if value > 1:
            question_number = list(vocab_df.loc[vocab_df[column] > 0, :].index)
            # 問題番号のずれを修正
            question_number = map(lambda x: x+4, question_number)
            duplicated_words[column] = (question_number)
    return duplicated_words


"""
1列目に出現数、2列目以降にその単語が出現した問題indexを格納したdfを返す
"""
def get_easy_check_df(duplicated_words):
    goal_df = pd.DataFrame(index=duplicated_words.keys(), data=duplicated_words.values())
    goal_df["count"] = goal_df.count(axis=1)
    goal_df = goal_df.sort_values("count", ascending=False)
    easy_check_df = pd.concat([goal_df.iloc[:,-1], goal_df.iloc[:,:-1]], axis=1)
    return easy_check_df


if __name__ == "__main__":
    df = pd.read_csv("data/mondai.csv", skiprows=2).dropna(thresh=5)
    bag_of_words = get_bag_of_words(df)
    all_vocablary = set(flatten(bag_of_words))

    vocab_df = get_vocab_df(df, bag_of_words, all_vocablary)
    duplicated_words = get_duplicated_words(vocab_df)
    easy_check_df = get_easy_check_df(duplicated_words)
    easy_check_df.to_csv("data/easy_check.csv")
