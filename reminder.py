"""
HipChatRoom 当番リマインダー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HipChat に当番のリマインダーを通知する。
"""

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
    def __init__(self, access_token, room_id,
                 endpoint='https://api.hipchat.com'):
        url = '{0}/v2/room/{1}/notification'.format(endpoint, room_id)
        req = Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer %s' % access_token)
        self.request = req

    def send_notification(self, message,
                          color='yellow', notify=False, message_format='html'):
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
    def __init__(self, name):
        self.task = name
        self.members = []

    def __repr__(self):
        return '<Assignment(task=%r, members=%r)>' % (self.task, self.members)


def load_yaml(yml_path):
    with open(yml_path) as f:
        return yaml.load(f)


def add_atmark(name):
    return '@' + name


def load_members_arrange(yml_path, iso_week):
    member_list = load_yaml(yml_path)
    mod = iso_week % len(member_list)
    splited_1 = member_list[:mod]
    splited_2 = member_list[mod:]
    return splited_2 + splited_1


def get_all_assignment_list(
        tasks_yml=DEFAULT_CONFIG['tasks_yml'],
        members_yml=DEFAULT_CONFIG['members_yml']):

    iso_week = date.today().isocalendar()[1]
    task_list = load_yaml(tasks_yml)
    member_list = load_members_arrange(members_yml, iso_week)

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

    for assignment in assignment_order_list:
        assignment['assignment'].members.append(member_list.pop(0))

    return assignment_list


def create_all_notification_message():
    all_assignment = get_all_assignment_list()

    msg = []

    msg.append('===== 今週の当番 =====')

    for assignment in all_assignment:
        msg.append('--- ' + assignment.task + ' ---')

        for member in assignment.members:
            msg.append(add_atmark(member))

        msg.append('')

    return '<br>'.join(msg)


def create_all_notification_job(hipchat_yml=DEFAULT_CONFIG['hipchat_yml']):
    def all_notification_job():
        msg = create_all_notification_message()
        hipchat_config = load_yaml(hipchat_yml)
        hipchat_room = HipChatRoom(
            hipchat_config['ACCESS_TOKEN'],
            hipchat_config['ROOM_ID']
        )
        hipchat_room.send_notification(msg)

    return all_notification_job


def create_notification_message(name, message):
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


def create_timed_job(name, message, hipchat_yml=DEFAULT_CONFIG['hipchat_yml']):
    hipchat_config = load_yaml(hipchat_yml)
    hipchat_room = HipChatRoom(
        hipchat_config['ACCESS_TOKEN'],
        hipchat_config['ROOM_ID']
    )

    def timed_job():
        msg = create_notification_message(name, message)
        hipchat_room.send_notification(msg)

    return timed_job


if __name__ == '__main__':
    sched = BlockingScheduler()

    task_list = load_yaml(DEFAULT_CONFIG['tasks_yml'])

    sched.add_job(
        create_all_notification_job(),
        **task_list['all']['schedule']
    )

    for task in task_list['tasks']:
        if 'schedules' in task:
            for schedule in task['schedules']:
                func = create_timed_job(task['name'], schedule['message'])
                sched.add_job(func, **schedule['schedule'])

    sched.start()
