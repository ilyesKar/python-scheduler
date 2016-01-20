import os
import pickle

import pika
import redis


BASE_KEY = 'watchdog:json:'
WATCHDOG_QUEUE = 'watchdog'


def add_key_to_redis(file_name, file_content):
    r = redis.StrictRedis()
    r.set(BASE_KEY + file_name, file_content)


def update_key_in_redis(file_name, file_content):
    add_key_to_redis(file_name, file_content)


def delete_key_from_redis(file_name):
    r = redis.StrictRedis()
    r.delete(BASE_KEY + file_name)


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