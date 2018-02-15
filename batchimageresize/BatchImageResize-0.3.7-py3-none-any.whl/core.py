from time import time
from shutil import copy
from os import walk, makedirs, path
from PIL import Image
from queue import Queue
from threading import Lock
from .utils import start_threads


class Resizer:
    """Класс для изменения размеров и сжатия изображений"""
    def __init__(self, input_dir, output_dir, size, quality):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.size = size
        self.quality = quality
        self.task_queue = Queue()
        self.counter = 0
        self.task_count = None
        self.is_alive = True
        self.todo_dirs = []
        self.counter_lock = Lock()

    def find_tasks(self):
        """
        Готовим очередь заданий для обработки.
        :return:
        """
        for (dirpath, dirnames, filenames) in walk(self.input_dir):
            dst_dir = self.output_dir + dirpath.replace(self.input_dir, '')
            for fname in filenames:
                if fname[-3:].lower() in ['jpg', 'jpeg', 'png']:
                    task = {'fname': fname,
                            'src_dir': dirpath,
                            'dst_dir': dst_dir}
                    self.task_queue.put(task)
            self.todo_dirs.append(dst_dir)
        self.task_count = self.task_queue.qsize()

    def convert_image(self, src, dst):
        """
        Конвертируем и сохраняем изображение
        :param src: Полный путь до исходного изображения
        :param dst: Полный путь до сконвертированного изображения
        :return:
        """
        image = Image.open(src)
        image_format = image.format
        maxwidth, maxheight = self.size
        width, height = image.size
        ratio = min(maxwidth/width, maxheight/height)
        if ratio < 1:
            size = (int(ratio * width), int(ratio * height))
            image = image.resize(size, Image.ANTIALIAS)
            if image_format == 'JPEG':
                image.save(dst, quality=self.quality)
            elif image_format == 'PNG':
                image.save(dst, compress_level=9)
        else:
            copy(src, dst)

    def make_dirs(self):
        """
        Создаем каталог, если если он не существует.
        :param dst_dir:
        :return:
        """
        for dst_dir in self.todo_dirs:
            if not path.exists(dst_dir):
                makedirs(dst_dir)

    def run(self):
        """
        Готовим задания.
        Запускаем потоки обработки по числу процессоров в системе и ждем из завершения.
        :return:
        """
        start_time = time()
        self.find_tasks()
        self.make_dirs()
        for thread in start_threads(self.convert):
            thread.join()
        return round(time() - start_time, 3)

    def progress(self, src):
        with self.counter_lock:
            self.counter += 1
            count = self.counter
        percent = str(count * 100 // self.task_count)
        self.show_progress(src, percent, count, self.task_count)

    def show_progress(self, src, percent, count, total_count):
        pass

    def convert(self):
        """
        Берем задание из очереди и запускаем конвертацию.
        :return:
        """
        try:
            while not self.task_queue.empty() and self.is_alive:
                task = self.task_queue.get()
                src_dir = task['src_dir']
                dst_dir = task['dst_dir']
                fname = task['fname']
                src = path.join(src_dir, fname)
                dst = path.join(dst_dir, fname)
                self.progress(src)
                self.convert_image(src, dst)
        except KeyboardInterrupt:
            self.is_alive = False
