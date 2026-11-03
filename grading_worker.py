from multiprocessing.queues import SimpleQueue

import grading

tracks: SimpleQueue = SimpleQueue()
active: bool = True


def worker():
    while active:
        item = tracks.get()