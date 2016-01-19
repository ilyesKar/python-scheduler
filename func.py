import requests
from celery_task_example import add

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

add.delay(4, 4)