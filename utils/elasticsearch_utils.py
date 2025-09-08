import logging
from elasticsearch import Elasticsearch, helpers
from .database import es, index_name
import uuid
import datetime

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
            actions = []
            for doc in documents:
                # 自动生成唯一的ES文档ID，如果文档中没有指定
                # 格式: question_{随机字符串}_{时间戳}
                if not doc.get('question_id'):
                    timestamp = int(datetime.datetime.now().timestamp())
                    random_str = uuid.uuid4().hex[:8]
                    es_id = f"question_{random_str}_{timestamp}"
                    doc['question_id'] = es_id
                else:
                    # 如果文档中已有question_id，则使用它作为ES文档ID
                    es_id = doc['question_id']
                    
                # 确保ingest_time字段存在
                if not doc.get('ingest_time'):
                    doc['ingest_time'] = datetime.datetime.now().isoformat()
                
                action = {
                    "_index": self.index_name,
                    "_id": es_id,  # 使用生成的ID作为ES文档ID
                    "_source": doc
                }
                actions.append(action)

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
