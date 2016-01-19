import time
from redis import Redis
from rq import Queue
from rq_worker_example import conn

from func import count_words_at_url

q = Queue(connection=conn)
job = q.enqueue(count_words_at_url, 'http://nvie.com')

print(job.result)   # => None

# Now, wait a while, until the worker is finished
time.sleep(3)
print(job.result)   # => 889