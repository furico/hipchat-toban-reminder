# HipChat当番リマインダー

## 開発環境の構築

Pythonのバージョンは3.4.2です。

開発用のパッケージをインストールします。

```
$ pip install -r requirements/dev.txt
```

## 実行方法

後述する設定ファイルを記述して実行します。

```
$ python reminder.py
```

### Herokuでの運用方法

設定ファイルを記述して、gitリポジトリに追加し、Herokuにpushすれば使えます。
