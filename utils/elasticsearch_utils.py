"""
Elasticsearch工具模块
"""
import logging
from elasticsearch import helpers
from .database import es, index_name

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Elasticsearch服务类"""

    @staticmethod
    def create_index(index_name_param=None):
        """创建索引"""
        try:
            # 使用传入的索引名或默认索引名
            target_index = index_name_param or index_name
            
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
            
            if not es.indices.exists(index=target_index):
                es.indices.create(index=target_index, body=mapping)
                logger.info(f"索引 {target_index} 创建成功")
                return True
            else:
                logger.info(f"索引 {target_index} 已存在")
                return False
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise

    @staticmethod
    def bulk_index(documents):
        """批量索引文档"""
        try:
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_source": doc
                }
                actions.append(action)
            
            success, failed = 0, 0
            for ok, result in helpers.streaming_bulk(es, actions, chunk_size=100):
                if ok:
                    success += 1
                else:
                    failed += 1
                    logger.error(f"索引失败: {result}")
            
            logger.info(f"批量索引完成: 成功 {success}, 失败 {failed}")
            return success, failed
        except Exception as e:
            logger.error(f"批量索引失败: {str(e)}")
            raise

    @staticmethod
    def search_by_id(question_id):
        """根据ID搜索"""
        try:
            result = es.get(index=index_name, id=question_id)
            return result.get("_source", {})
        except Exception as e:
            logger.error(f"根据ID搜索失败: {str(e)}")
            raise

    @staticmethod
    def search_by_content(keyword, size=10, from_=0):
        """根据内容搜索"""
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
            result = es.search(index=index_name, body=query)
            return result.get("hits", {})
        except Exception as e:
            logger.error(f"根据内容搜索失败: {str(e)}")
            raise

    @staticmethod
    def list_all(size=100, from_=0):
        """列出所有文档"""
        try:
            query = {
                "query": {
                    "match_all": {}
                },
                "size": size,
                "from": from_
            }
            result = es.search(index=index_name, body=query)
            return result.get("hits", {})
        except Exception as e:
            logger.error(f"列出所有文档失败: {str(e)}")
            raise 