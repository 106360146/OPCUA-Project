#!/usr/bin/python3
import inspect
from datetime import datetime
import traceback, sys
import hashlib

def calculate_file_md5(to_be_hashed):
    m = hashlib.md5()
    with open(to_be_hashed, "rb") as fptr:
        buf = fptr.read()
        m.update(buf)

    return m.hexdigest()

class __LINE__(object):
    def __repr__(self):
        try:
            raise Exception
        except:
            import sys
            return str(sys.exc_info()[2].tb_frame.f_back.f_lineno)

__LINE__ = __LINE__()

class dprint():
    def __init__(self, *argv):
        try:
            raise Exception
        except:
            import sys
            self.line = str(sys.exc_info()[2].tb_frame.f_back.f_lineno)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        frm = inspect.stack()[1]
        self.mod_name = inspect.getmodule(frm[0]).__name__
        print(f'[{timestamp}][{self.mod_name}: {self.line}] {argv}')


def errTraceback(e):
    rv = list()
    error_class = e.__class__.__name__
    detail = e.args[0]
    _, _, tb = sys.exc_info()

    last = traceback.extract_tb(tb)[-1]
    for lastCallStack in traceback.extract_tb(tb):
        filepath = lastCallStack[0]
        moduleName = filepath.split('/')[-1]
        if moduleName == '__init__.py':
            moduleName = filepath.split('/')[-2]

        lineNum = lastCallStack[1]
        funcName = lastCallStack[2]

        if last != lastCallStack:
            errMsg = f"[{moduleName}: {lineNum}][{funcName}]"
        else:
            errMsg = f"[{moduleName}: {lineNum}][{funcName}][{error_class}] {detail}"

        rv.append(errMsg)

    return rv
