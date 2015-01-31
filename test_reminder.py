"""Tests for Reminder."""

import unittest
import reminder


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

if __name__ == '__main__':
    unittest.main()
