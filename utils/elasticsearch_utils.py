import logging
from elasticsearch import Elasticsearch, helpers
from .database import es, index_name

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
        self.index_name = "questions"

    def count_documents(self):
        try:
            count_response = self.es.count(index=self.index_name)
            return count_response.get('count', 0)
        except Exception as e:
            logger.error(f"获取文档总数失败: {e}")
            return 0

    def list_all(self, from_=0, size=20):
        try:
            query = {
                "query": {
                    "match_all": {}
                },
                "size": size,
                "from": from_
            }
            result = self.es.search(index=self.index_name, body=query)
            return result  # 返回原始完整响应，调用者自行解析
        except Exception as e:
            logger.error(f"列出所有文档失败: {e}")
            return {"hits": {"hits": [], "total": {"value": 0}}}

    def create_index(self, index_name_param=None):
        try:
            target_index = index_name_param or self.index_name
            
            mapping = {
                "mappings": {
                    "properties": {
                        "question_id": {"type": "keyword"},
                        "content": {"type": "text", "analyzer": "ik_max_word"},
                        "question_type": {"type": "keyword"},
                        "difficulty": {"type": "keyword"},
                        "answer": {"type": "text"},
                        "options": {
                            "type": "nested",
                            "properties": {
                                "text": {"type": "text"},
                                "image": {"type": "keyword"},
                                "is_image": {"type": "boolean"}
                            }
                        },
                        "explanation": {"type": "text"},
                        "source": {"type": "keyword"},
                        "ingest_time": {"type": "date"}
                    }
                }
            }
            
            if not self.es.indices.exists(index=target_index):
                self.es.indices.create(index=target_index, body=mapping)
                logger.info(f"索引 {target_index} 创建成功")
                return True
            else:
                logger.info(f"索引 {target_index} 已存在")
                return False
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
            raise

    def bulk_index(self, documents):
        try:
            actions = [{
                "_index": self.index_name,
                "_source": doc
            } for doc in documents]

            success, failed = 0, 0
            for ok, result in helpers.streaming_bulk(self.es, actions, chunk_size=100):
                if ok:
                    success += 1
                else:
                    failed += 1
                    logger.error(f"索引失败: {result}")

            logger.info(f"批量索引完成: 成功 {success}, 失败 {failed}")
            return success, failed
        except Exception as e:
            logger.error(f"批量索引失败: {e}")
            raise

    def search_by_id(self, question_id):
        try:
            result = self.es.get(index=self.index_name, id=question_id)
            return result.get("_source", {})
        except Exception as e:
            logger.error(f"根据ID搜索失败: {e}")
            raise

    def search_by_content(self, keyword, size=10, from_=0):
        try:
            query = {
                "query": {
                    "match": {
                        "content": keyword
                    }
                },
                "size": size,
                "from": from_
            }
            result = self.es.search(index=self.index_name, body=query)
            return result.get("hits", {})
        except Exception as e:
            logger.error(f"根据内容搜索失败: {e}")
            raise
