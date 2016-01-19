import requests
from celery_task_example import add
import os
import redis


BASE_KEY = "json:"


def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())


def add_key_to_redis(path):
    r = redis.StrictRedis()
    json_file = open(path, "rb").read()
    r.set(BASE_KEY + os.path.basename(path), json_file)


def update_key_in_redis(path):
    add_key_to_redis(path)


def delete_key_from_redis(path):
    r = redis.StrictRedis()
    r.delete(BASE_KEY + os.path.basename(path))

add.delay(4, 4)