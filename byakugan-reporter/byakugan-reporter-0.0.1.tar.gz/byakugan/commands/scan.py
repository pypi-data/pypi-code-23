"""The scan command."""
from json import dumps
from os.path import abspath, dirname, join

import cv2

from byakugan.helpanto.ip_scanner_h import scan_ip_address
from .base import Base
from ..helpanto import md_h as md


class Scan(Base):
    """Scan IP address"""

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.data = []
        self.all_ip = scan_ip_address(self.options['--ip'])
        self.result = ''
        self.result_path = './'

    def run(self):
        print('You have the following options:', dumps(self.options, indent=2, sort_keys=True))
        # TODO need to change directory to user home
        this_dir = abspath(dirname(__file__))

        if self.options['--out_dir'] == "current_dir":
            self.result_path = join(this_dir, 'list_ip_camera.md')
        else:
            self.result_path = join(self.options['--out_dir'], 'list_ip_camera.md')
        self.prepare_data()

        self.generate_markdown()

        with open(self.result_path, 'w', encoding='utf-8') as f:
            f.write(self.result)

    def prepare_data(self):
        for ip in self.all_ip:
            attempted = 0
            url = 'rtsp://admin:admin@' + ip + ':80/live'
            filename = 'camera_' + ip.split('.')[-1]
            cap = cv2.VideoCapture(url)
            file_path = self.options['--out_dir'] + '/img' + filename + '.png'
            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(file_path, frame)
                    cap.release()
                    print('Successfully saved:', filename)
                    self.data.append({'ip': ip, 'file_path': file_path})
                    break
                else:
                    attempted += 1
                    print('attempting:', attempted)
                    if attempted == 10:
                        print('Failed to saved:', filename)
                        cap.release()
                        break
                    continue

    def generate_markdown(self):
        self.result += md.h1('List of IP Camera in KIT', new_line=2)
        self.result += md.horizontal_bar()
        for index, camera in enumerate(self.data):
            md.h5(str(index + 1) + '. ' + camera.get('ip'), new_line=1)
            md.img(camera.get('file_path'))
        print('Done')
