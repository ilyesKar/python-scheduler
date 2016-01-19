import logging
import sys
import time
import os

import redis
from daemon import DaemonContext
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


BASE_KEY = "json:"

class FileChangeHandler(FileSystemEventHandler):

    def __init__(self, logger):
        self.logger = logger

    def on_modified(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("modified = " + str(event.src_path))
            r = redis.StrictRedis()
            img = open(event.src_path,"rb").read()
            r.set(BASE_KEY + os.path.basename(event.src_path),img)

    def on_created(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("created = " + str(event.src_path))
            r = redis.StrictRedis()
            img = open(event.src_path,"rb").read()
            r.set(BASE_KEY + os.path.basename(event.src_path),img)

    def on_deleted(self, event):
        if event.src_path[-5:] == ".json":
            self.logger.debug("deleted = " + str(event.src_path))
            r = redis.StrictRedis()
            r.delete(BASE_KEY + os.path.basename(event.src_path))


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