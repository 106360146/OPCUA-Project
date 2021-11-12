#!/usr/bin/python

'''
    Log data to console and/or files if needed

    Authors:
    Ike Tien   <ike.tien@pioneerm.com>

    Copyright (c) 2018 Pioneer Machinery
'''

import os
import logging
import logging.handlers

from utility.utility_arg_process import log_classes_process
from utility.utility_debug import dprint

LOG_FILE = f"log/syslog.log"
LOG_FORMAT = '[%(asctime)s][%(module)s: %(lineno)d][%(name)s][%(levelname)s] \"%(message)s\"'
C_FORMAT = '[%(asctime)s][%(module)s: %(lineno)d][%(name)s][$BOLD%(levelname)s$RESET] \"$BOLD%(message)s$RESET\"'

LEVELS = {
    'notset': logging.NOTSET,
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL,
}
#######################################################################################
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

# Ref: https://blog.phpgao.com/python_colorful_log.html
#######################################################################################

class LOG(object):
    def __init__(self, logger_name, log_level='notset', log_path=LOG_FILE, log_mode='a', logger_format=LOG_FORMAT):
        self.logger_name = logger_name

        '''
            Create logger and set its level. Note that the same
            logger name refers to the same instance if exists.
        '''
        self.logger = logging.getLogger(logger_name)

        level = LEVELS.get(log_level.lower(), logging.NOTSET)
        self.logger.setLevel(level)

        COLOR_FORMAT = formatter_message(C_FORMAT, True)
        color_formatter = ColoredFormatter(COLOR_FORMAT)

        # Create console/file handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        rfh = logging.handlers.RotatingFileHandler( \
            filename=log_path, mode=log_mode, maxBytes=100000, backupCount=2)
        rfh.setLevel(logging.DEBUG)

        # add formatter to 'ch'/'rfh'
        formatter = logging.Formatter(logger_format, "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(color_formatter)
        rfh.setFormatter(formatter)

        # Remove handler before adding it. This is becasue logger
        # might exist before creating.
        for h in self.logger.handlers:
            self.logger.removeHandler(h)

        # Add ch/fh to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(rfh)

    def getLogger(self):
         return logging.getLogger(self.logger_name)

class LOG_INFORMATION():
    def __init__(self, default_log_level, log_classes):
        logging = LOG(logger_name=__class__.__name__, log_level='debug', log_path=f"log/{__class__.__name__}.log")
        self.logger = logging.getLogger()

        self.default_log_level = default_log_level
        self.log_classes = log_classes_process( log_classes )
        self.class_loggers = dict()

    def __get_log_level(self, class_name):
        level = self.log_classes.get( class_name, self.default_log_level ).lower()
        if level not in LEVELS:
            self.logger.warn(f"name of log level '{level}' not in {list(LEVELS)}, uses default level: {self.default_log_level}")
            return f"{self.default_log_level}"
        return f'{level}'

    def init_class_logger(self, class_name):
        log_level = self.__get_log_level( class_name )

        if class_name not in self.class_loggers:
            logging = LOG(logger_name=class_name, log_level=log_level, log_path=f"log/{class_name}.log")
            self.class_loggers[class_name] = logging

        logger = self.class_loggers[class_name].getLogger()
        return logger

