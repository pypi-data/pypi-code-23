"""Parser for Troitsk Rsh data files."""

import os
import struct
import sys
from datetime import datetime

import dateutil
import numpy as np

from df_data.type_codes import (channel_control, synchro_channel_control,
                                synchro_channel_types, synchro_control)

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
if CUR_DIR not in sys.path:
    sys.path.append(CUR_DIR)
del CUR_DIR



def serialise_to_rsh(params: dict) -> str:
    """Преобразование конфигурационного файла в формате JSON в текстовый хедер.

    rsh. Хедер можно использовать как конфигурационный файл для lan10-12base
    @params -- параметры в формате JSON (dfparser.def_values.DEF_RSH_PARAMS)
    @return -- текстовый хедер

    """
    out = "// Generated at %s\n\n" % (datetime.now())

    def add_val(field, value):
        """Add value to multiple line in rsh format."""
        if isinstance(value, bytes):
            value = value.decode("cp1251")
        val = ''.join('%s, ' % (v) for v in value) if isinstance(value, list) \
              else value
        if isinstance(val, str) and val.endswith(', '):
            val = val[:-2]
        return '%s -- %s\n' % (val, field)

    for param in params:
        if param == "channel":
            for i, channel in enumerate(params[param]):
                for ch_par in channel:
                    val = "%s_%s[%s]" % (param, ch_par, i)
                    if ch_par == "params":
                        val = "%ss_%s[%s]" % (param, ch_par, i)

                    out += add_val(val, channel[ch_par])
        elif param == "synchro_channel":
            for sync_ch_par in params[param]:
                if sync_ch_par == "type":
                    out += add_val(param, params[param][sync_ch_par])
                else:
                    out += add_val("%s_%s" % (param, sync_ch_par),
                                   params[param][sync_ch_par])
        else:
            out += add_val(param, params[param])

    return out


def parse_from_rsb(header: bytearray) -> dict:
    """Парсинг бинарного хедера rsb в JSON.

    @header -- бинарный хедер (2048 bytes)
    @return -- параметры в формате JSON (dfparser.def_values.DEF_RSH_PARAMS)

    """
    params = {}

    params["text_header_size"] = struct.unpack('I', header[0:4])[0]

    params["events_num"] = struct.unpack('i', header[8:12])[0]

    start_time = struct.unpack('Q', header[16:24])[0]
    params["start_time"] = datetime.fromtimestamp(start_time).isoformat()
    end_time = struct.unpack('Q', header[24:32])[0]
    params["end_time"] = datetime.fromtimestamp(end_time).isoformat()

    params["filepath"] = header[32: 32 + 255].rstrip(b'\0').decode("cp1251")

    params["num_blocks"] = struct.unpack('i', header[288:292])[0]

    params["aquisition_time"] = struct.unpack('i', header[292:296])[0]

    params["blocks_in_file"] = struct.unpack('i', header[296:300])[0]

    params["waitTime"] = struct.unpack('i', header[300:304])[0]

    params["threshold"] = struct.unpack('d', header[312:320])[0]

    sync_params_num = struct.unpack('I', header[336:340])[0]
    sync_params = np.unique(np.frombuffer(header[320:336], np.uint32)
                            [:sync_params_num])
    params["synchro_control"] = []
    for param in sync_params:
        if param == 0:
            params["synchro_control"].append("Default")
        else:
            params["synchro_control"].append(list(synchro_control.keys())
                                             [list(synchro_control.values())
                                              .index(param)])

    params["sample_freq"] = struct.unpack('d', header[344:352])[0]
    params["pre_history"] = struct.unpack('I', header[352:356])[0]

    params["packet_number"] = struct.unpack('i', header[356:360])[0]

    params["b_size"] = struct.unpack('I', header[360:364])[0]

    params["hysteresis"] = struct.unpack('I', header[364:368])[0]

    params["channel_number"] = struct.unpack('I', header[368:372])[0]

    ch_params = []

    for i in range(params["channel_number"]):
        ch_data = header[372 + 56 * i: 372 + 56 * (i + 1)]
        ch_param = {}

        param_num = struct.unpack('I', ch_data[36:40])[0]
        ch_params_raw = np.unique(np.frombuffer(ch_data[4:36],
                                                np.uint32)[:param_num])
        ch_param["params"] = []
        for param in ch_params_raw:
            if param == 0:
                ch_param["params"].append("Default")
            else:
                ch_param["params"].append(list(channel_control.keys())
                                          [list(channel_control.values())
                                           .index(param)])

        ch_param["adjustment"] = struct.unpack('d', ch_data[44:52])[0]
        ch_param["gain"] = struct.unpack('I', ch_data[52:56])[0]
        ch_params.append(ch_param)

    params["channel"] = ch_params

    synchro_channel = {}
    sync_ch_par_num = struct.unpack('I', header[632:636])[0]
    sync_ch_params_raw = np.unique(np.frombuffer(header[600:632],
                                                 np.uint32)[:sync_ch_par_num])

    synchro_channel["params"] = []
    for param in sync_ch_params_raw:
        if param == 0:
            synchro_channel["params"].append("Default")
        else:
            synchro_channel["params"] \
                .append(list(synchro_channel_control.keys())
                        [list(synchro_channel_control.values()).index(param)])

    synchro_channel_type = struct.unpack('I', header[304:308])[0]
    synchro_channel["type"] = list(synchro_channel_types.keys())[
        list(synchro_channel_types.values()).index(synchro_channel_type)]

    synchro_channel["gain"] = struct.unpack('I', header[636:640])[0]

    params["synchro_channel"] = synchro_channel

    params["err_lang"] = struct.unpack('I', header[640:644])[0]
    params["board_name"] = header[644:644 + 255].rstrip(b'\0').decode("cp1251")

    params["board_id"] = struct.unpack('I', header[900:904])[0]

    return params


def serialize_to_rsb(params: dict) -> bytes:
    """Сериализация JSON хедера rsb.

    @params -- параметры в формате JSON (dfparser.def_values.DEF_RSH_PARAMS)
    @return -- бинарный хедер (2048 bytes)

    """
    header = bytearray(np.zeros(2048, np.byte).tostring())

    if "text_header_size" in params:
        header[0:4] = struct.pack('I', params["text_header_size"])

    if "events_num" in params:
        header[8:12] = struct.pack('i', params["events_num"])

    if "start_time" in params:
        start_time = dateutil.parser.parse(params["start_time"]).timestamp()
        header[16:24] = struct.pack('Q', int(start_time))

    if "end_time" in params:
        end_time = dateutil.parser.parse(params["end_time"]).timestamp()
        header[24:32] = struct.pack('Q', int(end_time))

    header[32:32 + len(params["filepath"])
           ] = params['filepath'].encode('cp1251')

    header[288:292] = struct.pack('i', params["num_blocks"])

    header[292:296] = struct.pack('i', int(params["aquisition_time"]))

    header[296:300] = struct.pack('i', params["blocks_in_file"])

    header[300:304] = struct.pack('i', int(params["waitTime"]))

    header[312:320] = struct.pack('d', params["threshold"])

    sync_params = params["synchro_control"]
    sync_params_num = len(sync_params)

    header[336:340] = struct.pack('I', sync_params_num)

    for i in range(sync_params_num):
        if sync_params[i] == 'Default':
            code = 0
        else:
            code = synchro_control[sync_params[i]]

        header[320 + i * 4:320 + (i + 1) * 4] = struct.pack('I', code)

    header[344:352] = struct.pack('d', params["sample_freq"])
    header[352:356] = struct.pack('I', params["pre_history"])

    header[356:360] = struct.pack('i', params["packet_number"])

    header[360:364] = struct.pack('I', params["b_size"])

    header[364:368] = struct.pack('I', params["hysteresis"])

    header[368:372] = struct.pack('I', params["channel_number"])

    for i in range(params["channel_number"]):
        off = 372 + 56 * i

        ch_param = params['channel'][i]

        header[off + 44: off + 52] = struct.pack('d', ch_param["adjustment"])
        header[off + 52: off + 56] = struct.pack('I', ch_param["gain"])
        header[off + 36: off + 40] = struct.pack('I', len(ch_param['params']))

        for j, param in enumerate(ch_param['params']):
            if param == 'Default':
                code = 0
            else:
                code = channel_control[param]
                header[off + 4 + j * 4:
                       off + 4 + (j + 1) * 4] = struct.pack('I', code)

    synchro_channel = params['synchro_channel']
    header[632:636] = struct.pack('I', len(synchro_channel['params']))

    for i, param in enumerate(synchro_channel['params']):
        if param == 'Default':
            code = 0
        else:
            code = synchro_channel_control[param]
            header[600 + i * 4: 600 + (i + 1) * 4] = struct.pack('I', code)

    sync_type = synchro_channel_types[synchro_channel['type']]
    header[304:308] = struct.pack('I', sync_type)

    header[636:640] = struct.pack('I', synchro_channel["gain"])

    if "err_lang" in params:
        header[640:644] = struct.pack('I', params["err_lang"])

    if "board_name" in params:
        header[644:644 + len(params["board_name"])] = \
            params['board_name'].encode('cp1251')

    if "board_id" in params:
        header[900: 904] = struct.pack('I', params["board_id"])

    return bytes(header)


def dump_to_rsb(params: dict, times: np.ndarray, data: np.ndarray) -> bytes:
    """Сохранение данных в формате rsb.

    @params -- параметры набора
    @times -- абсолютные времена блоков в наносекундах
    @data -- данные блоков (block_num, block_size)

    @return -- сериализованные данные

    """
    assert isinstance(times, np.ndarray)
    assert times.ndim == 1
    assert isinstance(data, np.ndarray)
    assert data.ndim == 2
    assert len(data) == len(times)

    params['b_size'] = data.shape[1]
    params['events_num'] = data.shape[0]

    start = int(times.min() * 1e-9)
    end = int(times.max() * 1e-9)

    if 'start_time' not in params:
        params['start_time'] = datetime.fromtimestamp(start).isoformat()

    if 'end_time' not in params:
        params['end_time'] = datetime.fromtimestamp(end).isoformat()

    text_header = bytearray(5120)
    text = serialise_to_rsh(params).encode('cp1251')
    text_header[:len(text)] = text

    params['text_header_size'] = len(text)

    binary_header = serialize_to_rsb(params)

    bin_data = b''

    ch_num = params['channel_number']
    ev_size = params['b_size']
    for i, event_data in enumerate(data):
        event = bytearray(
            np.zeros(96 + 2 * ch_num * ev_size, np.byte).tostring())
        text_hdr = datetime.fromtimestamp(int(times[i] * 10e-9)).isoformat()

        event[:len(text_hdr)] = text_hdr.encode('cp1251')
        event[64:68] = struct.pack('I', i)
        event[72:80] = struct.pack('Q', int(times[i] * 10e-9))
        event[80:88] = struct.pack('Q', int(times[i]))

        event[96:] = event_data.astype(np.int16).tostring()
        bin_data += event

    return bytes(text_header + binary_header + bin_data)


class RshPackage(object):
    """Rsh package object."""

    def __init__(self, file):
        """Load from file or fp.

        @file -- filename or opened file
        """
        if isinstance(file, str):
            self.file = open(file, "rb+")
        else:
            self.file = file

        self.file.seek(0)

        self.text_header = self.file.read(5120).decode("cp1251").rstrip('\0')

        header = self.file.read(2048)
        self.params = parse_from_rsb(header)

    def get_event(self, num):
        """Extract event from dataset."""
        if num < 0 or num >= self.params["events_num"]:
            raise IndexError("Index out of range [0:%s]" %
                             (self.params["events_num"]))

        ch_num = self.params['channel_number']
        ev_size = self.params['b_size']

        event = {}

        self.file.seek(7168 + num * (96 + 2 * ch_num * ev_size))

        event["text_hdr"] = self.file.read(64)
        event["ev_num"] = struct.unpack('I', self.file.read(4))[0]
        self.file.read(4)

        start_time = struct.unpack('Q', self.file.read(8))[0]
        event["start_time"] = datetime.fromtimestamp(start_time)
        ns_since_epoch = struct.unpack('Q', self.file.read(8))[0]
        if ns_since_epoch:
            event['ns_since_epoch'] = ns_since_epoch
        self.file.read(8)

        event_data = self.file.read(2 * ev_size * ch_num)

        event["data"] = np.fromstring(event_data, np.short)

        return event

    def update_event_data(self, num, data):
        """Update event data in dataset."""
        if num < 0 or num >= self.params["events_num"]:
            raise IndexError("Index out of range [0:%s]" %
                             (self.params["events_num"]))

        if isinstance(data, np.ndarray):
            raise TypeError("data should be np.ndarray")

        if data.dtype != np.short:
            raise TypeError("data array dtype should be dtype('int16')")

        ch_num = self.params['channel_number']
        ev_size = self.params['b_size']

        if data.shape != (ch_num * ev_size,):
            raise Exception("data should contain same number of elements "
                            "(%s)" % (ch_num * ev_size))

        self.file.seek(7168 + num * (96 + 2 * ch_num * ev_size) + 96)
        self.file.write(data.tostring())
        self.file.flush()
