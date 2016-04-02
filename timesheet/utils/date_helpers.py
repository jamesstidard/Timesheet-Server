from datetime import datetime
import time

__author__ = 'James Stidard'


def parse_unix_time(value, javascript=False):
    if javascript:
        value /= 1000
    return datetime.fromtimestamp(int(value))


def to_unix_time(value, javascript=False):
    value = time.mktime(value.timetuple())
    if javascript:
        value *= 1000
    return value
