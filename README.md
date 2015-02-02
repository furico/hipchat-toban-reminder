# HipChat当番リマインダー

当番を忘れないように、Hipchatにリマインダーを送るスクリプトです。

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

## 設定ファイル

config配下に以下のファイルを用意します。
既にサンプルファイルが入っているのでそれをリネームすればひな形として使えます。

* hipchat.yml
* members.yml
* tasks.yml

### hipchat.yml

### members.yml

### tasks.yml
