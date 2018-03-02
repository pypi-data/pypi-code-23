# coding=utf-8
import progressbar
import tarfile
from enum import Enum
from checksumdir import dirhash

try:
    import _thread
except ImportError:
    import thread as _thread
import shutil
import websocket
from russell.client.base import RussellHttpClient
from russell.cli.utils import *
from russell.log import logger as russell_logger
from russell.exceptions import *


SOCKET_STATE = Enum('State', 'INIT UPLOADING FINISH FAILED')


class FsClient(RussellHttpClient):

    def __init__(self):
        self.ws_url = "ws://{host}:{port}".format(host=russell.russell_fs_host,
                                                  port=russell.russell_fs_port)
        self.FILE_NAME = ''
        self.STATE = SOCKET_STATE.INIT
        super(FsClient, self).__init__()

    def on_message(self, ws, message):
        russell_logger.debug(ws.header)
        russell_logger.debug(message)
        def start_sending(*args):
            with open(self.FILE_NAME, 'rb') as f:
                # with progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))) as bar:
                bar = progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))).start()
                try:
                    total_uploaded_size = 0
                    block_size = 1024 * 1024
                    msg = f.read(block_size)
                    while msg:
                        total_uploaded_size += len(msg)
                        ws.sock.send_binary(msg)
                        msg = f.read(block_size)
                        bar.update(total_uploaded_size)
                except:
                    pass
                finally:
                    pass

        russell_logger.debug('received {}'.format(message))
        resp_json = json.loads(message)
        code = resp_json.get('code')
        if code == 200: # to be modified
            if self.STATE == SOCKET_STATE.INIT:
                self.STATE = SOCKET_STATE.UPLOADING
                russell_logger.info('Start uploading...')
                _thread.start_new_thread(start_sending, ())
            else:
                self.STATE = SOCKET_STATE.FINISH
                ws.close()
        elif code == 522:
            self.STATE = SOCKET_STATE.FAILED
            raise OverPermissionException()
        elif code == 532:
            self.STATE = SOCKET_STATE.FAILED
            raise RussellException()
        elif code == 533:
            self.STATE = SOCKET_STATE.FAILED
            raise OverSizeException()
        elif code == 529:
            self.STATE = SOCKET_STATE.FAILED
            raise NotFoundException()
        elif code == 506:
            self.STATE = SOCKET_STATE.FAILED
            raise AuthenticationException()
        elif code == 507:
            self.STATE = SOCKET_STATE.FAILED
            raise AuthenticationException('Login expired!')
        else:
            self.STATE = SOCKET_STATE.FAILED
            raise ServiceBusyException()

    def clear_archive(self):
        shutil.rmtree(self.temp_dir)

    def on_error(self, ws, error):
        self.STATE = SOCKET_STATE.FAILED
        russell_logger.debug(str(error))
        ws.close()
        if isinstance(error, ClickException):
            # raised from on_message
            raise error

    def on_close(self, ws):
        self.clear_archive()
        russell_logger.debug('close connection to server')

    def on_open(self, ws):
        russell_logger.debug('setup connection to server')

    def socket_upload(self, file_type, filename, access_token, file_id, user_name, data_name, temp_dir="./temp", is_compress=True):
        self.module_id = file_id
        # compress the folder
        russell_logger.info('compressing files...')
        self.temp_dir = temp_dir
        try:
            self.FILE_NAME = shutil.make_archive(base_name=os.path.join(temp_dir, file_id),
                                                 format='gztar' if is_compress else 'tar',
                                                 root_dir=filename,
                                                 owner=None,
                                                 group=None,
                                                 logger=russell_logger)
        except Exception as e:
            raise e
        # compute md5 checksum
        hash_code = get_md5_checksum(self.FILE_NAME)
        compressed_size = os.path.getsize(self.FILE_NAME)
        russell_logger.info("compressed size: {} Bytes".format(compressed_size))

        # setup connection
        # websocket.enableTrace(True)
        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/{}/{}/".format(file_type, file_id),
            header={
                'access_token': access_token,
                'size': str(compressed_size),
                'hash_code': hash_code,
                'user_name': user_name,
                'data_name': data_name,
                'is_compress': str(is_compress)
            },
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def socket_upload_tar(self, file_type, filename, access_token, file_id, user_name, data_name, temp_dir="./temp", is_compress=True):
        self.module_id = file_id
        # compress the folder
        russell_logger.info('compressing files...')
        self.temp_dir = temp_dir
        try:
            with tarfile.open(os.path.join(temp_dir, file_id), "w:gz" if is_compress else "w") as tar:
                ignore_list, whitelist = RussellIgnoreManager.get_list()
                ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
                ignore = ignore_patterns(*ignore_list_expanded)
                names = os.listdir(filename)
                if ignore is not None:
                    ignored_names = ignore(filename, names)
                else:
                    ignored_names = set()
                exclude_files = [os.path.join(filename, n) for n in ignored_names]
                tar.add(filename, filter=lambda x: None if x.name in exclude_files else x)
            self.FILE_NAME = os.path.join(temp_dir, file_id)
            # self.FILE_NAME = shutil.make_archive(base_name=os.path.join(temp_dir, file_id),
            #                                      format='gztar' if is_compress else 'tar',
            #                                      root_dir=filename,
            #                                      owner=None,
            #                                      group=None,
            #                                      logger=russell_logger)
        except Exception as e:
            raise e
        # compute md5 checksum
        hash_code = get_md5_checksum(self.FILE_NAME)
        compressed_size = os.path.getsize(self.FILE_NAME)
        russell_logger.info("compressed size: {} Bytes".format(compressed_size))

        # setup connection
        # websocket.enableTrace(True)
        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/{}/{}/".format(file_type, file_id),
            header={
                'access_token': access_token,
                'size': str(compressed_size),
                'hash_code': hash_code,
                'user_name': user_name,
                'data_name': data_name,
                'is_compress': str(is_compress)
            },
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def get_state(self):
        return self.STATE