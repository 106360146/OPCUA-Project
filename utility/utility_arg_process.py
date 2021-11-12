#!/usr/bin/python3
'''
    This moudle Handles arguments from main.py
'''

def log_classes_process( log_classes ):
    result = dict()
    temp = [ x.strip() for x in log_classes.split(',') ]
    for x in temp:
        rv = x.split(':')
        if len(rv) == 2:
            result[rv[0]] = rv[1]
    return result


