"""
HipChatRoom 当番リマインダー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HipChat に当番のリマインダーを通知する。
"""

import os
import json
import yaml
from datetime import date
from urllib.request import Request, urlopen
from operator import itemgetter
from apscheduler.schedulers.blocking import BlockingScheduler

DEFAULT_CONFIG = {
    'tasks_yml': 'config/tasks.yml',
    'members_yml': 'config/members.yml',
    'hipchat_yml': 'config/hipchat.yml',
}


class HipChatRoom:
    """HipChatに接続するクラス

    :param access_token: HipChatのアスセストークン
    :param room_id: 通知を送るHipChatのルームID
    :param endpoint: APIのエンドポイント
    """

    def __init__(self, access_token, room_id,
                 endpoint='https://api.hipchat.com'):
        url = '{0}/v2/room/{1}/notification'.format(endpoint, room_id)
        req = Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer %s' % access_token)
        self.request = req

    def send_notification(self, message,
                          color='yellow', notify=False, message_format='html'):
        """ルームに通知を送る。
        パラメータはHipChatのAPIに従う。
        https://www.hipchat.com/docs/apiv2/method/send_room_notification

        :param message: 送信するメッセージ
        :param color: メッセージの背景色
        :param notif: メッセージが送信されたことをユーザに通知するかどうか
        :param message_format: HipChat内でのレンダリング方式
        """
        body = {
            'message': message,
            'color': color,
            'notify': notify,
            'message_format': message_format,
        }
        json_data = json.dumps(body)
        params = json_data.encode('utf8')

        return urlopen(self.request, params)


class Assignment:
    """当番の割り当てを表すクラス

    :param name: 当番のタスク名
    """

    def __init__(self, name):
        self.task = name
        self.members = []

    def __repr__(self):
        return '<Assignment(task=%r, members=%r)>' % (self.task, self.members)


def load_yaml(yml_path):
    """ymlファイルを読み込む。"""
    with open(yml_path) as f:
        return yaml.load(f)


def add_atmark(name):
    """先頭に@マークを付与する。"""
    return '@' + name


def arrange_list(ls, index):
    """リストを並び変える。
    indexの位置でリストを分割し、前後を入れ替える。

    :param ls: list
    :param index: 分割位置
    """
    splited_1 = ls[:index]
    splited_2 = ls[index:]
    return splited_2 + splited_1


def get_all_assignment_list(
        tasks_yml=DEFAULT_CONFIG['tasks_yml'],
        members_yml=DEFAULT_CONFIG['members_yml']):
    """当番を割り当てたリストを取得する。
    タスクリストとメンバーリストを読み込む。
    タスクリストのorderと現在日付が１年の何週目かに応じて、
    それぞれのタスクにメンバーを割り当て、そのリストを返却する。

    :param tasks_yml: タスク設定ファイルのパス
    :param members_yml: メンバー設定ファイルのパス
    """
    task_list = load_yaml(tasks_yml)
    assignment_list = []
    assignment_order_list = []

    for task in task_list['tasks']:
        assignment = Assignment(task['name'])
        assignment_list.append(assignment)
        assignment_order_list.extend(
            [dict(assignment=assignment, order=o) for o in task['order']]
        )

    assignment_order_list = \
        sorted(assignment_order_list, key=itemgetter('order'))

    iso_week = date.today().isocalendar()[1]
    mod = iso_week % len(assignment_order_list)
    assignment_order_list = arrange_list(assignment_order_list, mod)

    member_list = load_yaml(members_yml)

    for i, member in enumerate(member_list):
        assignment = assignment_order_list[i]['assignment']
        assignment.members.append(member)

    return assignment_list


def create_all_notification_message():
    """全体通知用のメッセージを作成する。"""
    all_assignment = get_all_assignment_list()

    msg = []

    msg.append('===== 今週の当番 =====')

    for assignment in all_assignment:
        msg.append('--- ' + assignment.task + ' ---')

        for member in assignment.members:
            msg.append(add_atmark(member))

        msg.append('')

    return '<br>'.join(msg)


def create_all_notification_job(hipchat_room):
    """全体通知用のジョブを作成する。

    :param hipchat_room: HipChatRoomオブジェクト
    """
    def all_notification_job():
        msg = create_all_notification_message()
        hipchat_room.send_notification(msg)

    return all_notification_job


def create_notification_message(name, message):
    """個別タスク通知用のメッセージを作成する。

    :param name: タスク名
    :param message: メッセージ
    """
    all_assignment = get_all_assignment_list()

    msg = []

    for assignment in all_assignment:
        if assignment.task == name:
            target_assignment = assignment
            break

    msg.append('--- ' + name + ' ---')
    msg.append(message)
    for member in target_assignment.members:
        msg.append(add_atmark(member))

    return '<br>'.join(msg)


def create_timed_job(name, message, hipchat_room):
    """個別タスク通知用のジョブを作成する。

    :param name: タスク名
    :param message: メッセージ
    :param hipchat_room: HipChatRoomオブジェクト
    """
    def timed_job():
        msg = create_notification_message(name, message)
        hipchat_room.send_notification(msg)

    return timed_job


if __name__ == '__main__':
    # HipChatへの接続設定
    hipchat_access_token = os.getenv('HIPCHAT_ACCESS_TOKEN')
    hipchat_room_id = os.getenv('HIPCHAT_ROOM_ID')

    if hipchat_access_token is None:
        hipchat_config = load_yaml(DEFAULT_CONFIG['hipchat_yml'])
        hipchat_access_token = hipchat_config['ACCESS_TOKEN']

    if hipchat_room_id is None:
        hipchat_config = load_yaml(DEFAULT_CONFIG['hipchat_yml'])
        hipchat_room_id = hipchat_config['ROOM_ID']

    hipchat_room = HipChatRoom(
        hipchat_access_token,
        hipchat_room_id
    )

    sched = BlockingScheduler()
    task_list = load_yaml(DEFAULT_CONFIG['tasks_yml'])

    # 全体通知用のジョブを追加
    sched.add_job(
        create_all_notification_job(hipchat_room),
        **task_list['all']['schedule']
    )

    # 個別タスク通知用のジョブを追加
    for task in task_list['tasks']:
        if 'schedules' in task:
            for schedule in task['schedules']:
                func = create_timed_job(
                    task['name'],
                    schedule['message'],
                    hipchat_room)
                sched.add_job(func, **schedule['schedule'])

    sched.start()
