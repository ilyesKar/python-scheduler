import os
import pickle

import pika


WATCHDOG_QUEUE = 'watchdog'


def send_to_scheduler(event, path):
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