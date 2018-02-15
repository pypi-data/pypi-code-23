import sys

import pytest
from mock import patch

from iotlab_radio_test.draw_common import DrawArgs
from iotlab_radio_test.cli import main
from iotlab_radio_test.config import get_config_from_yaml, get_exp_dir, get_raw_dir, get_parsed_dir, \
    get_image_dir
from iotlab_radio_test.constants import LOG_DIR
from iotlab_radio_test.start import get_api

exp_dirs = {}
raw_dirs = {}
parsed_dirs = {}
image_dirs = {}

for i in [1, 141, 142, 143, 144, 145,
          'test_name', 'test2_name', 10, 11, 12, 13, 14]:
    exp_dirs[i] = get_exp_dir(i)
    raw_dirs[i] = get_raw_dir(exp_dirs[i])
    parsed_dirs[i] = get_parsed_dir(exp_dirs[i])
    image_dirs[i] = get_image_dir(exp_dirs[i])

ENTRY = 'iotlab_radio_test.cli.%s_main'

config = get_config_from_yaml()
draw_args = DrawArgs('pdr', None, False, False, False, False)

commands = [
    (['run', '-i', '141'],
     [config, exp_dirs[141], raw_dirs[141], 9000]),
    (['clean', '-i', '145'],
     [get_image_dir(exp_dirs[145]), parsed_dirs[145]]),
    (['raw_parser', '-i', '142'],
     [config, raw_dirs[142], parsed_dirs[142]]),
    (['connectivity', '-i', '143'],
     [config, parsed_dirs[143]]),
    (['aggregate_stability', '-l', '10','11','12', '-n', 'test_name'],
     [config, LOG_DIR, parsed_dirs['test_name'], [10, 11, 12], 'test_name']),
    (['aggregate_avg', '-l', '13','14', '-n', 'test2_name'],
     [config, LOG_DIR, parsed_dirs['test2_name'], [13, 14], 'test2_name']),
    (['draw', '-i', '144'],
     [config, image_dirs[144], parsed_dirs[144], draw_args])
]

calls = [c[0:1] for c in commands]
ids =[c[0][0] for c in commands]


@pytest.mark.parametrize(['cmd'], calls, ids=ids)
def test_entrypoints_called(cmd):
    with patch(ENTRY % cmd[0]) as mock2:
        testargs = ['prog'] + cmd
        with patch.object(sys, 'argv', testargs):
            main()

            assert mock2.called


@pytest.mark.parametrize(['cmd', 'expectedargs'], commands, ids=ids)
def test_entrypoints_callargs(cmd, expectedargs):
    with patch(ENTRY % cmd[0]) as mock2:
        testargs = ['prog'] + cmd
        with patch.object(sys, 'argv', testargs):
            main()
            mock2.assert_called_once_with(*expectedargs)


def test_keyboard_interrupt():
    def side_effect(*args, **kwargs):
        raise KeyboardInterrupt

    with patch(ENTRY % 'start', side_effect=side_effect) as mock2:
        testargs = ['prog', 'start']
        with patch.object(sys, 'argv', testargs):
            ## the keyboard interrupt should be caught
            main()
