#/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
"""
This file runs an HTTP server on port 8001. When you connect to it, you'll
get an infinite stream of random JSON objects, with no delimiter between them.
"""

from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults
import random
import json
import sys


if sys.version_info.major >= 3:
    unichr = chr


def make_random_characters():
    def random_char():
        if random.randint(0, 9):
            return unichr(random.randrange(0, 0xd800))
        else:
            return unichr(random.randrange(0xe000, 0x110000))
    return ''.join(random_char() for i in range(random.randint(1, 4)))


def make_random_scalar():
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            'yes', 'no', 'maybe', ':)', '', float('nan'), float('inf'),
            float('-inf'), '🁵🂊🂇',
            '[{"This looks like JSON": "but it\'s actually a string"}]',
            "'", '"', "hello, world", '{', '}', '[',
            ']', "back\\slash", "\\\"\\\\", "\x00", "漢字", -1, 0, 1, 2, 3, 5,
            8, 0.0, 10000, 3.14159, 6.02e23, 1e-30, True, False, None
        ])


def make_random_string():
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            '', 'a', 'um', 'foo', 'quack', ',', ':', '"',
        ])


def make_random_dict(depth=0):
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return {make_random_string(): make_random_value(depth + i)
            for i in range(length)}


def make_random_list(depth=0):
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return [make_random_value(depth + i) for i in range(length)]


def make_random_value(depth=0):
    choice = random.randint(0, 4)
    if choice == 1:
        return make_random_list(depth)
    elif choice == 2:
        return make_random_dict(depth)
    else:
        return make_random_scalar()


def make_random_json():
    value = make_random_dict()
    indent = random.choice([None, None, None, None, None, None, 1, 2])
    ensure_ascii = random.choice([True, False])
    separators = random.choice([
        (", ", ": "),
        (", ", ": "),
        (", ", ": "),
        (",", ": "),
        (", ", ":"),
        (",", ":"),
        (" , ", " : "),
        ("  ,", ":  ")
    ])
    return json.dumps(value, indent=indent, ensure_ascii=ensure_ascii,
                      separators=separators)


def make_random_chunk_size():
    choice = random.randint(0, 1)
    if choice == 0:
        return random.choice([0, 1, 4, 1024])
    else:
        return random.randint(0, 1024)


def generate_chunks():
    """
    Generate an infinite, chunked stream of bytes. These bytes will form valid
    JSON objects, but the boundaries of the chunks are not in any way aligned
    with the boundaries of the JSON objects.

    Each chunk will contain 0 to 1024 bytes, inclusive.
    """
    random.seed(0)
    buf = b''
    while True:
        chunk_size = make_random_chunk_size()
        while len(buf) < chunk_size:
            buf += make_random_json().encode('utf-8')
        to_send = buf[:chunk_size]
        buf = buf[chunk_size:]
        yield to_send


def application(environ, start_response):
    """
    The very simple WSGI application that runs this server.
    """
    setup_testing_defaults(environ)

    # You may wonder why I'm taking these strings and running them through
    # the str() constructor.
    #
    # It's because WSGI requires all headers to be *native* strings -- that
    # is, whatever type str() is in this version of Python, even if the rest
    # of the code is set up to use Unicode by default.
    headers = [
        (str('Content-Type'), str('application/x-json-stream')),
    ]
    start_response(str('200 OK'), headers)
    for chunk in generate_chunks():
        yield chunk


if __name__ == '__main__':
    srv = make_server('localhost', 8001, application)
    srv.serve_forever()

