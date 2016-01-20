import logging
import pickle
import traceback

import pika
import redis
from daemon import DaemonContext
from rq import Queue

from scheduler_functions import delete_key_from_redis, add_key_to_redis

WATCHDOG_QUEUE = 'watchdog'


def watchdog_callback(ch, method, properties, body):
    q = Queue(connection=redis.Redis())
    body_content = pickle.loads(body)
    if body_content.get('event') == 'deletion':
        q.enqueue(delete_key_from_redis, body_content.get('fileName'))
    else:
        q.enqueue(add_key_to_redis, body_content.get('fileName'), body_content.get('file'))


def run_watchdog_consumer():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("./scheduler_watchdog.log")
    logger.addHandler(fh)
    with DaemonContext(files_preserve=[fh.stream, ], ):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
            channel = connection.channel()

            channel.queue_declare(queue=WATCHDOG_QUEUE)

            channel.basic_consume(watchdog_callback,
                                  queue=WATCHDOG_QUEUE,
                                  no_ack=True)
            channel.start_consuming()
        except:
            print(traceback.format_exc())
            logger.error("error # " + traceback.format_exc())


def run():
    run_watchdog_consumer()


if __name__ == "__main__":
    run()