"""Tests aind_labtracks_service methods."""

import unittest

from aind_labtracks_service import message_handlers


class MessageHandlerTest(unittest.TestCase):
    """Tests MessageHandler methods."""

    my_msg = "Hello World!!"
    p = message_handlers.MessageHandler(my_msg)

    def test_log_msg(self):
        """Tests that the log_msg method logs a message."""
        with self.assertLogs() as captured:
            self.p.log_msg()

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), self.my_msg)


if __name__ == "__main__":
    unittest.main()
