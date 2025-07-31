from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
index_name = "questions"

def inspect_data(size=5):
    try:
        res = es.search(
            index=index_name,
            body={
                "query": {"match_all": {}},
                "size": size
            }
        )
        hits = res.get("hits", {}).get("hits", [])
        print(f"共查到{len(hits)}条数据，打印前{size}条：")
        for i, hit in enumerate(hits, 1):
            print(f"--- 第{i}条 ---")
            print(hit["_source"])
            print()
    except Exception as e:
        print(f"查询失败: {e}")

if __name__ == "__main__":
    inspect_data()
