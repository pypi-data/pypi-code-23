"""I/O utilities"""
import json
import logging


def stream_json_file(local_file):
    """Stream a JSON file (in JSON-per-line format)

    Args:
        local_file (file-like object) an open file-handle that contains a
            JSON string on each line
    Yields:
        (dict) JSON objects
    """
    for i, line in enumerate(local_file):
        try:
            data = json.loads(line.decode('utf-8'))
            yield data
        except ValueError as e:
            logging.warning("Skipping line %d due to error: %s", i, e)
            continue
