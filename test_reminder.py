"""Tests for Reminder."""

import unittest
import reminder


class ReminderTestCase(unittest.TestCase):
    def test_add_atmark(self):
        result = reminder.add_atmark('test')
        self.assertEqual('@test', result)

if __name__ == '__main__':
    unittest.main()
