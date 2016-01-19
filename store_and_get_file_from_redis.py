import redis

r = redis.Redis()
json_file = open("/home/nabil/Téléchargements/watch/test1.json", "rb").read()
# print(json_file)
r.set("test:test1.json", json_file)
# print(r.get("test:test1.json"))
json_file = open("/home/nabil/test1.json", "w").write(r.get("test:test1.json").decode("utf-8"))