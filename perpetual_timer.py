import threading
from queue import Queue

on_pause = False
url_queue = Queue()


class perpetual_timer():
    """ Класс, экземпляр которырого вызывает hFunction каждые t млс"""

    def __init__(self, t, hFunction, pos_offset):
        self.t = t
        self.pos_offset = pos_offset
        self.hFunction = hFunction
        self.job = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        """функция, руководящая выполнением переданной функции,
        а также переопределяющая таймер для следующего
        периода """
        if not on_pause:
            with threading.Lock():
                new_args = url_queue.get()
            self.hFunction(new_args, self.pos_offset)
            self.pos_offset = None
        self.job = threading.Timer(self.t, self.handle_function)
        self.job.start()


def on_release(key):
    global on_pause
    try:
        if key.vk == 80:
            on_pause = not on_pause
    except AttributeError:
        print("Invalid Key")
