import os
import json
from datetime import datetime
from elasticsearch import Elasticsearch
import redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "./views/config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

redis_conf = config["redis"]
rename_map = config.get("rename_map", {})
allowed_fields = set(rename_map.values())
index_name = config.get("index_name", "questions")

client = redis.StrictRedis(
    host=redis_conf["host"],
    port=redis_conf["port"],
    db=redis_conf["db"],
    password=redis_conf["password"],
    decode_responses=True
)

es = Elasticsearch("http://localhost:9200")


def get_question_id():
    date_key = datetime.now().strftime("qid:%Y%m%d")
    num = client.incr(date_key)
    client.expire(date_key, 2 * 24 * 60 * 60)
    return f"{datetime.now().strftime('%Y%m%d')}{num:04d}"
