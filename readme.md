# usage
data/mondai.csv
に問題文が入ったファイルを入れる。
（なお、3行目から問題文が始まることや、"問題文"　という列名が付けられていることを仮定している。後々汎用性があるように直すかも）
あとvenv環境で動くかどうか試してない
```
source venv/bin/activate
python main.py
```
でdata/easy_check.csvが生成されているはず。
