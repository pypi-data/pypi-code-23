import unittest
import shutil, tempfile, os

from terminaltables import AsciiTable

from ..storage import Storage

def file_empty(file):
    return not bool(os.path.getsize(file))

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.sv_list = [
            {
                "username": "pi",
                "ip": "192.168.0.134",
                "name": "sween",
                "location": "Dining Room"
            },
            {
                "username": "pi",
                "ip": "192.168.0.169",
                "name": "brewpi-prod",
                "location": "Brew Rig"
            }
        ]
        self.temp_dir = tempfile.mkdtemp()
        self.st = Storage(testing = True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        to_remove = [self.st.file_path, self.st.file_path + '.bak']
        for fi in to_remove:
            if os.path.isfile(fi):
                os.remove(fi)

    def test_create_file(self):
        file_path = os.path.join(self.temp_dir, "test_file")
        assert not os.path.isfile(file_path)
        self.st.create_file(file_path)
        assert os.path.isfile(file_path)
        os.remove(file_path)

    def test_create_file_in_protected_dir(self):
        file_path = '/bin/junc_test_file'
        assert not os.path.isfile(file_path)
        with self.assertRaises(PermissionError):
            self.st.create_file(file_path)
        assert not os.path.isfile(file_path)

    def test_write(self):
        assert file_empty(self.st.file_path)
        self.st.write(self.sv_list)
        assert not file_empty(self.st.file_path)

    def test_get_server_list(self):
        # Intentionally leaving the file empty
        assert self.st.get_servers() == []

        # Write some data to retrieve later
        assert file_empty(self.st.file_path)
        self.st.write(self.sv_list)
        assert not file_empty(self.st.file_path)

        server_list = self.st.get_servers()
        assert server_list == self.sv_list

    def test_backup(self):
        backup_file = self.st.file_path + '.bak'
        if os.path.isfile(backup_file):
            os.remove(backup_file)
        assert not os.path.isfile(backup_file)
        self.st.backup()
        assert os.path.isfile(backup_file)

    def test_restore(self):
        self.st.backup()
        assert os.path.isfile(self.st.file_path + '.bak')
        if os.path.isfile(self.st.file_path):
            os.remove(self.st.file_path)

        assert not os.path.isfile(self.st.file_path)
        self.st.restore()
        assert os.path.isfile(self.st.file_path)






