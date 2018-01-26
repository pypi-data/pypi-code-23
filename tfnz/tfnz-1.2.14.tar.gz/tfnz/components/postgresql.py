# Copyright (c) 2018 David Preece, All rights reserved.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from tfnz.location import Location
from tfnz.container import Container
from tfnz.volume import Volume


class Postgresql:
    @staticmethod
    def spawn(location: Location, volume: Volume, *, log_callback=None) -> Container:
        node = location.node()
        ctr = node.spawn_container('tfnz/postgresql',
                                   sleep=True,
                                   volumes=[(volume, '/var/lib/postgresql')]).wait_until_ready()
        ctr.run_process('openrc', data_callback=log_callback)
        ctr.run_process('touch /run/openrc/softlevel')
        ctr.run_process('openrc-run /etc/init.d/postgresql start',
                        data_callback=log_callback, stderr_callback=log_callback)
        return ctr
