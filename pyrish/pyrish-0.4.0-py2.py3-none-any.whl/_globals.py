LINUX = 'Linux'
OSX = 'Darwin'
WINDOWS = 'Windows'

SYS_PATH = '/'
PUBLIC_DNS = '8.8.8.8'
LOCALHOST = '127.0.0.1'

CPU_MODEL_LINUX_CMD = "cat /proc/cpuinfo | grep 'model name' | sort -u | cut -d: -f2"
CPU_MODEL_OSX_CMD = "sysctl -n machdep.cpu.brand_string"
