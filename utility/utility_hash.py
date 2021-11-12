#!/usr/bin/python3
import hashlib

def calculate_file_md5(to_be_hashed):
    m = hashlib.md5()
    with open(to_be_hashed, "rb") as fptr:
        buf = fptr.read()
        m.update(buf)

    return m.hexdigest()

def md5_str(to_be_hashed):
    if isinstance(to_be_hashed, str):
        m = hashlib.md5()
        m.update( to_be_hashed.encode() )
        return m.hexdigest()
    else:
        raise ValueError(f"Invalid type of argument: {to_be_hashed}")
