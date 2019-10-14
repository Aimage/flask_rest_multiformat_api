# -*- coding: utf-8 -*-

import datetime


DATE_UNIX_START = datetime.datetime.strptime("01-01-1990 00:00:00", '%d-%m-%Y %H:%M:%S')


def date_to_str_fr(date):
    return datetime.datetime.strftime(date, '%d-%m-%Y %H:%M:%S')


def date_format_validator_fr(str):
    try:
        date = datetime.datetime.strptime(str, '%d-%m-%Y %H:%M:%S')
        return date > DATE_UNIX_START
    except ValueError:
        return False
    return True


def fr_date_str_to_date(date_str):
    date = datetime.datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S') if date_format_validator_fr(date_str) else None
    return date 