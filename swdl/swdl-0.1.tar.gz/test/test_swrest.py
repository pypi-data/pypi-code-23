import pytest
from swdl import swrest
import json
import os
from swdl.matches import NoPlaylistError, NoEndlistError
from swdl.matches import FFMPegRunner

@pytest.fixture
def data_service():
    cred_file= os.environ.get("SW_CREDENTIAL_FILE","")
    credentials = json.loads(open(cred_file).read())
    account = credentials["username"]
    password = credentials["password"]
    return swrest.DataService(account, password)


def test_get_match(data_service):
    m = data_service.get_match(1300)
    assert m.match_id == 1300


def test_get_match_from_string(data_service):
    m = data_service.get_match("1300")
    assert m.match_id == 1300


def test_update_match(data_service):
    m = data_service.get_match(1300)
    m.pull_info()
    assert m.match_id == 1300


def test_get_matches(data_service):
    m = data_service.get_matches()
    assert len(m) > 0


def test_update_labels(data_service):
    m = data_service.get_match(1300)
    m.pull_labels()
    num_pos = m.labels.positions.shape[0]
    num_events = m.labels.events.shape[0]
    num_status = m.labels.status.shape[0]
    assert num_pos > 1
    assert num_events > 1
    assert num_status > 1
    m.pull_labels()
    assert num_pos == m.labels.positions.shape[0]
    assert num_events == m.labels.events.shape[0]
    assert num_status == m.labels.status.shape[0]

#@pytest.mark.skip(reason="Will take much to long")
def test_download_full_match(data_service):
    m = data_service.get_match(1300)
    m.download_user_stream()

def test_download_match_no_playlist(data_service):
    with pytest.raises(NoPlaylistError):
        m = data_service.get_match(4636)
        m.download_user_stream()

def test_download_match_no_endlist(data_service):
    with pytest.raises(NoEndlistError):
        m = data_service.get_match(4634)
        m.download_grid_stream()

def test_match_endlist(data_service):
    m = data_service.get_match(4634)
    assert m.grid_stream_has_endlist() == False
    assert m.user_stream_has_endlist() == True

    m = data_service.get_match(1300)
    assert m.grid_stream_has_endlist() == True
    assert m.user_stream_has_endlist() == True

def test_find_duration():
    test_string =  " Duration: 02:29:56.61, start: 3630.021300, bitrate: 0 kb/s"
    duration = int(FFMPegRunner.find_duration(test_string))
    assert duration == 2*60*60+29*60+56

def test_find_position():
    test_string="frame=   50 fps=0.0 q=-1.0 Lsize=     776kB time=02:02:02.71 bitrate=2345.6kbits/s speed=2.75x "
    position = int(FFMPegRunner.find_position(test_string))
    assert position == 2*60*60+2*60+2
