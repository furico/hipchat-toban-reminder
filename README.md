# HipChat当番リマインダー

当番を忘れないように、Hipchatにリマインダーを送るスクリプトです。

週が変わると、設定ファイルにしたがって当番の割り当ても自動で変わります。

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

HipChatの情報を記述します。

アクセストークンと通知を送るルームIDを記述します。

```yaml
---
ACCESS_TOKEN: <access_token>
ROOM_ID: <room_id>
```

アクセストークは[ここ](https://www.hipchat.com/account/api)で入手します。

### members.yml

当番を割り当てるメンバーのリストです。

このリストに記述した名前で@mentionが送られます。

そのため@mention name を記述してください。

```yaml
---
# member
- <membar1>
- <membar2>
- <membar3>
```

### tasks.yml

当番、割り当てる順番、通知メッセージについて記述します。

サンプルファイルを元に解説します。

```yaml
---
all:
  schedule:
    trigger: interval
    seconds: 5
tasks:
  -
    name: 燃えるゴミ
    order: [50, 90]
    schedules:
      -
        schedule:
          trigger: interval
          seconds: 5
        message: 明日は燃えるゴミの日です。ゴミのまとめをお願いします。
      -
        schedule:
          trigger: interval
          seconds: 7
        message: 今日は燃えるゴミの日です。ゴミ出しをお願いします。
  -
    name: 資源ゴミ
    order: [30, 60, 80]
    schedules:
      -
        schedule:
          trigger: interval
          seconds: 11
        message: 明日は資源ゴミの日です。ゴミ出しをお願いします。
  -
    name: 掃除機
    order: [10]
  -
    name: シュレッダー
    order: [20]
  -
    name: 当番なし
    order: [40, 70]
```

#### all

割り当て一覧を通知します。

```yaml
all:
  schedule:
    trigger: interval
    seconds: 5
```

scheduleのtriggerはAPSchedulerのtriggersです。

したがって、[こちらにあるtriggers](https://apscheduler.readthedocs.org/en/latest/py-modindex.html)から選択できます。

上記の例ではintervalを選択したため、[対応するパラメータ](https://apscheduler.readthedocs.org/en/latest/modules/triggers/interval.html#module-apscheduler.triggers.interval)も合わせて設定します。

triggersにcronを設定した場合、対応するパラメータは[こちら](https://apscheduler.readthedocs.org/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron)です。

たとえば以下のように記述すると、毎週月曜日の午前10時に通知を送ることになります。

```yaml
schedule:
  trigger: cron
  day_of_week: mon
  hour: 10
```

#### tasks

tasksは当番のリストです。name、order、schedulesのリストになっています。

nameは当番の名前です。

orderは割り当ての順番であり、orderの要素数がその当番の割り当て人数です。

そのため、各taskのorderの要素数の合計がmembers.ymlの要素数と同じになる必要があります。

サンプルではorderの要素数の合計は9であるため、members.ymlも9でなければなりません。

orderを適度にバラけさせることで、連続で同じ当番に割当たらないようにできます。

schedulesは通知を送りたい場合に必要です。schedule、messageのリストになっています。

scheduleは前述と同じです。

messageは通知時に送るメッセージです。
当番に割り当てられているメンバーの@mentionが付与されて通知されます。

例えば以下のように記述すると、燃えるゴミに関する通知が水曜日の17時30分と木曜日の10時30分に送られます。

```yaml
name: 燃えるゴミ
order: [50, 90]
schedules:
  -
    schedule:
      trigger: cron
      day_of_week: wed
      hour: 17
      minute: 30
    message: 明日は燃えるゴミの日です。ゴミのまとめをお願いします。
  -
    schedule:
      trigger: cron
      day_of_week: thu
      hour: 10
      minute: 30
    message: 今日は燃えるゴミの日です。ゴミ出しをお願いします。
```

通知が不要であればschedulesは記述しなくてよいです。

以下の記述では、掃除機は個別の通知は行われません。

```yaml
name: 掃除機
order: [10]
```
