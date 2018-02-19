from buildlib.docker import cmd
from typing import Optional, Pattern, NamedTuple, Union, List
import re
import subprocess as sp
from buildlib.util import eprint


class Image(NamedTuple):
    num: int
    repository: str
    tag: str
    id: str
    created: str
    size: str


def get_images(
    repository: Optional[Union[bytes, str, Pattern]] = None,
    tag: Optional[Union[bytes, str, Pattern]] = None,
    id: Optional[Union[bytes, str, Pattern]] = None,
    created: Optional[Union[bytes, str, Pattern]] = None,
    size: Optional[Union[bytes, str, Pattern]] = None,
) -> Optional[List[Image]]:
    """"""
    kwargs = locals()
    result = sp.run(['docker', 'images'], stdout=sp.PIPE)

    output = result.stdout.decode()

    images = []
    new_images = []
    count = 0

    for raw_line in output.split('\n'):
        if raw_line:
            cols = re.split('[ \t]{3,}', raw_line)

        if cols[0] == 'REPOSITORY':
            continue

        if len(cols) == 5:
            images.append(
                Image(count, cols[0], cols[1], cols[2], cols[3], cols[4])
            )
            count += 1
        else:
            eprint('Error: cannot interpret line in output:\n' + raw_line)

    for image in images:
        for arg, val in kwargs.items():
            if val:
                if re.search(val, image.repository):
                    new_images.append(image)
                    continue
   
    return new_images or None
