"""Tests for Reminder."""

import unittest
import reminder
from datetime import date

TEST_CONFIG = {
    'tasks_yml': 'test/tasks.yml',
    'members_yml': 'test/members.yml',
    'date_today': date(2015, 6, 1),
}


class ReminderTestCase(unittest.TestCase):
    def test_add_atmark(self):
        result = reminder.add_atmark('test')
        self.assertEqual('@test', result)

    def test_arrange_list(self):
        ls = [1, 2, 3, 4, 5]
        index = 0
        result = reminder.arrange_list(ls, index)
        self.assertEqual([1, 2, 3, 4, 5], result)

        index = 2
        result = reminder.arrange_list(ls, index)
        self.assertEqual([3, 4, 5, 1, 2], result)

        index = len(ls) - 1
        result = reminder.arrange_list(ls, index)
        self.assertEqual([5, 1, 2, 3, 4], result)

    def test_get_all_assignment_list(self):
        result = reminder.get_all_assignment_list(
            TEST_CONFIG['tasks_yml'],
            TEST_CONFIG['members_yml'],
            TEST_CONFIG['date_today'])

        task_list = reminder.load_yaml(TEST_CONFIG['tasks_yml'])
        member_list = reminder.load_yaml(TEST_CONFIG['members_yml'])

        test_members = [
            [member_list[3], member_list[8]],
            [member_list[0], member_list[2], member_list[6]],
            [member_list[4]],
            [member_list[5]],
            [member_list[1], member_list[7]],
        ]

        self.assertEqual(len(task_list['tasks']), len(result))

        for i, assignment in enumerate(result):
            self.assertEqual(task_list['tasks'][i]['name'], assignment.task)
            self.assertEqual(test_members[i], assignment.members)

if __name__ == '__main__':
    unittest.main()
