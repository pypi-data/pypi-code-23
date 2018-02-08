# coding: utf8

import gevent
import time
import collections

import kcp_wrapper

from .log import logger
from .output_listener import OutputListener
from .timer import Timer


class Connection(object):

    output_listener_class = OutputListener

    # 检测过期
    expire_timer = None

    # kcp 检查的timer
    kcp_check_timer = None

    app = None
    sock = None
    address = None

    _read_buffer = None
    _read_buffer_size = None

    # 正在发送的buf的偏移量
    _write_buffer_offset = None
    # 发送队列
    _write_buffer = None

    kcp_obj = None

    _closed = None

    def __init__(self, app, sock, address):
        self._closed = False
        self.app = app
        self.sock = sock
        self.address = address

        self.expire_timer = Timer()
        self._set_expire_callback()

        self._write_buffer_offset = 0
        self._write_buffer = collections.deque()

        self._read_buffer = collections.deque()
        self._read_buffer_size = 0

        self.app.events.create_conn(self)

        self.kcp_obj = self._create_kcp_obj()
        self.kcp_check_timer = Timer()

    def _create_kcp_obj(self):
        """
        可以继承重写
        :return:
        """
        kcp_obj = kcp_wrapper.KcpWrapper(self.app.conv)
        # kcp_obj.setNoDelay(1, 10, 2, 1)
        kcp_obj.setOutputListener(self.output_listener_class(self.sock, self.address).__disown__())
        # mtu * size，size 就是包数量
        # kcp_obj.setWndSize(100, 100)

        return kcp_obj

    def get_now_time_ms(self):
        return int(time.time() * 1000) % 0xFFFFFFFF

    def kcp_check(self):
        """
        在send和input之后调用
        :return:
        """
        now = self.get_now_time_ms()

        # 调用input，需要重新check
        interval = self.kcp_obj.check(now) - now
        if interval < 0:
            interval = 0

        self.kcp_check_timer.set(interval / 1000.0, self._on_kcp_timer_ticked, force=True)

    def write(self, data):
        if isinstance(data, self.app.box_class):
            # 打包
            data = data.pack()
        elif isinstance(data, dict):
            data = self.app.box_class(data).pack()

        # 为了性能
        if not self._write_buffer:
            # 说明没有正在发送的消息
            self._write_buffer.append(data)
            self._write_buffer_offset = 0
            # 如果没有等待发送的buf，那么就立即去发送
            # 否则，就等到下一个可发送周期自动判断发送
            self._handle_write_buf()
        else:
            self._write_buffer.append(data)

    def close(self):
        """
        直接关闭连接
        """
        if self._closed:
            return

        # 关闭连接
        self._closed = True
            
        self._on_connection_close()

    def closed(self):
        """
        连接是否已经关闭
        :return:
        """
        return self._closed

    def handle(self, message):
        """
        启动处理
        """
        def inner_run():
            self.kcp_obj.input(message)
            self.kcp_check()

            while True:
                data = self.kcp_obj.recv()

                if data:
                    self._read_buffer.append(data)
                    self._read_buffer_size += len(data)
                else:
                    # 没有数据了才break
                    break

            if self._read_buffer_size:
                self._handle_read_buf()

        gevent.spawn(inner_run).join()

    def _on_connection_close(self):
        # 链接被关闭的回调

        self.app.remove_conn(self)

        self.kcp_check_timer.clear()
        # 这样才能保证释放
        self.kcp_obj = None

        self._clear_expire_callback()

        self.app.events.close_conn(self)

    def _on_read_complete(self, box):
        """
        数据获取结束
        data: 原始数据
        box: 解析后的box
        """

        # 每收到一次消息，就进行一次延后
        self._set_expire_callback()

        try:
            self.app.events.handle_request(self, box)
        except Exception, e:
            logger.error('view_func raise exception. box: %s, e: %s',
                         box, e, exc_info=True)

    def _handle_read_buf(self):
        while self._read_buffer:
            box = self.app.box_class()
            loc = box.unpack(self._read_buffer[0])
            if loc > 0:
                box._raw_data = self._consume(loc)
                self._on_read_complete(box)
                # 调用continue，继续寻找下一块

            elif loc < 0:
                # 说明接受的数据已经有问题了，直接把数据删掉
                logger.debug('buf check fail. ret: %d', loc)
                self._read_buffer_size -= len(self._read_buffer[0])
                self._read_buffer.popleft()

            else:
                # 还需要继续尝试
                if len(self._read_buffer) == 1:
                    break
                _double_prefix(self._read_buffer)

    def _consume(self, loc):
        if loc == 0:
            return b""
        _merge_prefix(self._read_buffer, loc)
        self._read_buffer_size -= loc
        return self._read_buffer.popleft()

    def _handle_write_buf(self):
        if not self._write_buffer:
            return

        while self._write_buffer:
            # 只要有队列
            head_buffer = self._write_buffer[0]

            ret = self.kcp_obj.send(head_buffer[self._write_buffer_offset:] if self._write_buffer_offset else head_buffer)
            if ret > 0:
                # 还是为了性能
                if (self._write_buffer_offset + ret) == len(head_buffer):
                    # 切换到下一个buf
                    self._write_buffer.popleft()
                    self._write_buffer_offset = 0
                else:
                    # 没有发送完
                    self._write_buffer_offset += ret
                    # 退出，无法再发了
                    break
            else:
                # 发不了了，那就直接退就好了
                break

        self.kcp_check()

    def _on_kcp_timer_ticked(self):
        self.kcp_obj.update(self.get_now_time_ms())
        self.kcp_check()

        if self._write_buffer:
            self._handle_write_buf()

    def _set_expire_callback(self):
        """
        注册超时的回调
        :return:
        """
        if self.app.timeout:
            # 超时了，就报错
            self.expire_timer.set(self.app.timeout, self._on_timeout)

    def _clear_expire_callback(self):
        self.expire_timer.clear()

    def _on_timeout(self):
        self.app.events.timeout_conn(self)
        self.close()

    def __repr__(self):
        return '<%s address: %s>' % (self.__class__.__name__, self.address)


def _double_prefix(deque):
    """Grow by doubling, but don't split the second chunk just because the
    first one is small.
    """
    new_len = max(len(deque[0]) * 2,
                  (len(deque[0]) + len(deque[1])))
    _merge_prefix(deque, new_len)


def _merge_prefix(deque, size):
    """Replace the first entries in a deque of strings with a single
    string of up to size bytes.

    >>> d = collections.deque(['abc', 'de', 'fghi', 'j'])
    >>> _merge_prefix(d, 5); print(d)
    deque(['abcde', 'fghi', 'j'])

    Strings will be split as necessary to reach the desired size.
    >>> _merge_prefix(d, 7); print(d)
    deque(['abcdefg', 'hi', 'j'])

    >>> _merge_prefix(d, 3); print(d)
    deque(['abc', 'defg', 'hi', 'j'])

    >>> _merge_prefix(d, 100); print(d)
    deque(['abcdefghij'])
    """
    if len(deque) == 1 and len(deque[0]) <= size:
        return
    prefix = []
    remaining = size
    while deque and remaining > 0:
        chunk = deque.popleft()
        if len(chunk) > remaining:
            deque.appendleft(chunk[remaining:])
            chunk = chunk[:remaining]
        prefix.append(chunk)
        remaining -= len(chunk)
    # This data structure normally just contains byte strings, but
    # the unittest gets messy if it doesn't use the default str() type,
    # so do the merge based on the type of data that's actually present.
    if prefix:
        deque.appendleft(type(prefix[0])().join(prefix))
    if not deque:
        deque.appendleft(b"")
