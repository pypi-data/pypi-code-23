# coding: utf8

NAME = 'ump'


# 单元的间隔时间
UNIT_INTERVAL = dict(
    hours=1
)

# 单元唯一标记
UNIT_FMT = '%Y%m%d%H.bill'

# 每次read的长度
BILL_READ_CHUNK_SIZE = 1024

# uploader在处理的时候，要记录pos
POS_FILENAME = 'pos'

# timestamp, offset
POS_FMT = '!qq'

# redis pop timeout
# 否则worker停止会失败
REDIS_POP_TIMEOUT = 1

# worker的env
WORKER_ENV_KEY = 'UMP_WORKER'

