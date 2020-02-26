import ast
import json
import logging
from json.decoder import WHITESPACE

import orjson

logger = logging.getLogger(__name__)


def iterload(string_or_fp, cls=json.JSONDecoder, **kwargs):
    """
    Source: https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python
    """
    if isinstance(string_or_fp, str):
        string = str(string_or_fp)
    else:
        string = string_or_fp.read()

    decoder = cls(**kwargs)
    idx = WHITESPACE.match(string, 0).end()
    while idx < len(string):
        retry_count = 3
        obj, end = None, None
        while retry_count > 0:
            try:
                obj, end = decoder.raw_decode(string, idx)
                break
            except Exception as e:
                retry_count -= 1

        yield obj
        if obj is None:
            idx = WHITESPACE.match(string, idx + 1).end()
        else:
            idx = WHITESPACE.match(string, end).end()


def iterload_file_lines(file):
    for line in file.readlines():
        try:
            json_object = orjson.loads(line)
            yield json_object
        except Exception as e:
            try:
                json_object = ast.literal_eval(line)
                yield json_object
            except Exception as e2:
                logger.warning("Could not parse line: %s. Errors: %s and: %s", line, e, e2)
                continue
