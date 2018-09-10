# coding=utf-8
import logging
import logging.handlers


class Logger:
    def __init__(self, name=__name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s")

        # stdout
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # fileout
        file = logging.handlers.RotatingFileHandler(
            filename='./log/cybex_digital_receipt.log',
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf8'
        )
        file.setLevel(logging.INFO)
        file.setFormatter(formatter)
        self.logger.addHandler(file)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
