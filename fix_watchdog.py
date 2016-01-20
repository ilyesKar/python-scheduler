import logging
import os
import pickle
import sys
import time

import pika
from daemon import DaemonContext
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

WATCHDOG_QUEUE = 'watchdog'


class FileChangeHandler(FileSystemEventHandler):

    def __init__(self, logger):
        self.logger = logger
        # self.q = Queue(connection=redis.Redis())

    def send_to_scheduler(self, event, path):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                           'localhost'))

        if event != 'deletion':
            body_content = {'event': event, 'fileName': os.path.basename(path), 'file': open(path).read()}
        else:
            body_content = {'event': event, 'fileName': os.path.basename(path)}

        channel = connection.channel()
        channel.queue_declare(queue=WATCHDOG_QUEUE)
        channel.basic_publish(exchange='',
                              routing_key=WATCHDOG_QUEUE,
                              body=pickle.dumps(body_content))
        connection.close()

    def on_modified(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("modified = " + str(event.src_path))
            # self.q.enqueue(update_key_in_redis, event.src_path)
            self.send_to_scheduler('modification', event.src_path)

    def on_created(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("created = " + str(event.src_path))
            # self.q.enqueue(add_key_to_redis, event.src_path)
            self.send_to_scheduler('creation', event.src_path)

    def on_deleted(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("deleted = " + str(event.src_path))
            # self.q.enqueue(delete_key_from_redis, event.src_path)
            self.send_to_scheduler('deletion', event.src_path)


def do_launch_main_program(logger):
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = FileChangeHandler(logger)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def run():
    # logging.basicConfig(filename="fix_watchdog.log", level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("./fix_watchdog.log")
    logger.addHandler(fh)
    with DaemonContext(files_preserve=[fh.stream, ], ):
        do_launch_main_program(logger)

if __name__ == "__main__":
    run()