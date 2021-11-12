#!/usr/bin/python3

import re

def validate_mac(mac):
    '''
        Validate MAC address. Return True as a valid MAC,
        False as invalid.

        RE:
        [0-9a-f] means an hexadecimal digit
        {2} means that we want two of them
        [-:]? means either a dash or a colon but optional.
            Note that the dash as first char doesn't mean a range but only means itself.
            This subexpression is enclosed in parenthesis so it can be reused later as a back reference.
        [0-9a-f]{2} is another pair of hexadecimal digits
        \\1 this means that we want to match the same expression, which is the expr inside (),
            that we matched before as separator. This is what guarantees uniformity.
            Note that the regexp syntax is \1 but I'm using a regular string so backslash must be escaped by doubling it.
        [0-9a-f]{2} another pair of hex digits
        {4} the previous parenthesized block must be repeated exactly 4 times,
            giving a total of 6 pairs of digits: <pair> [<sep>] <pair> ( <same-sep> <pair> ) * 4
        $ The string must end right after them
    '''
    if type(mac) == bytes:
        mac = mac.decode("utf-8")

    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        return True
    else:
        return False

def mac_add_separator(mac, sep=':'):

    mac_addr = ''

    if ':' in mac or '-' in mac:
        return ''

    if validate_mac(mac):
        for idx in range(0, 12, 2):
            mac_addr = mac_addr + sep + mac[idx: idx + 2]

        mac_addr = mac_addr[1:]
        return mac_addr

    return ''

def mac_remove_separator(mac):

    if validate_mac(mac):

        if len(mac) == 12:
            # means no separator
            return mac

        m = re.findall('[0-9a-z]{2}' , mac.lower())
        return ''.join(m)

    return ''

