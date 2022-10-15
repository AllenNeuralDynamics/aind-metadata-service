""" Module to handle printing messages to stdout.
"""

import logging


class MessageHandler:
    """
    Class to handle messages.
    """

    def __init__(self, msg):
        """
        Args:
            msg (str): Message to handle.
        """
        self.msg = msg

    def log_msg(self):
        """Simply logs the message."""
        logging.info(self.msg)
