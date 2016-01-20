import redis


BASE_KEY = 'watchdog:json:'


def add_key_to_redis(file_name, file_content):
    r = redis.StrictRedis()
    r.set(BASE_KEY + file_name, file_content)


def update_key_in_redis(file_name, file_content):
    add_key_to_redis(file_name, file_content)


def delete_key_from_redis(file_name):
    r = redis.StrictRedis()
    r.delete(BASE_KEY + file_name)
