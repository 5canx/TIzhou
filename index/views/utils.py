import logging
from datetime import datetime
from elasticsearch import Elasticsearch
import redis
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class DatabaseService:
    """数据库服务管理类"""

    _redis_instance = None
    _es_instance = None

    @classmethod
    def get_redis(cls):
        """获取Redis连接"""
        if cls._redis_instance is None:
            try:
                cls._redis_instance = redis.StrictRedis(
                    host=settings.REDIS_CONFIG['HOST'],
                    port=settings.REDIS_CONFIG['PORT'],
                    db=settings.REDIS_CONFIG['DB'],
                    password=settings.REDIS_CONFIG['PASSWORD'],
                    decode_responses=settings.REDIS_CONFIG['DECODE_RESPONSES'],
                    socket_timeout=settings.REDIS_CONFIG['SOCKET_TIMEOUT']
                )
                if not cls._redis_instance.ping():
                    raise ImproperlyConfigured("Redis连接测试失败")
                logger.info("Redis连接成功")
            except Exception as e:
                logger.error(f"Redis连接失败: {str(e)}")
                raise
        return cls._redis_instance

    @classmethod
    def get_es(cls):
        """获取Elasticsearch连接"""
        if cls._es_instance is None:
            try:
                cls._es_instance = Elasticsearch(
                    hosts=[settings.ES_CONFIG['HOST']],
                    timeout=settings.ES_CONFIG['TIMEOUT']
                )
                if not cls._es_instance.ping():
                    raise ImproperlyConfigured("Elasticsearch连接测试失败")
                logger.info("Elasticsearch连接成功")
            except Exception as e:
                logger.error(f"Elasticsearch连接失败: {str(e)}")
                raise
        return cls._es_instance


class QuestionIDGenerator:
    """问题ID生成器"""

    def __init__(self):
        self.redis = DatabaseService.get_redis()

    def generate(self):
        """生成唯一ID"""
        try:
            date_key = datetime.now().strftime("qid:%Y%m%d")
            num = self.redis.incr(date_key)
            self.redis.expire(date_key, 2 * 24 * 60 * 60)  # 2天过期
            return f"{datetime.now().strftime('%Y%m%d')}{num:04d}"
        except Exception as e:
            logger.error(f"生成问题ID失败: {str(e)}")
            raise RuntimeError("问题ID生成失败")


# 初始化服务
try:
    # 数据库连接
    redis_client = DatabaseService.get_redis()
    es_client = DatabaseService.get_es()

    # 工具类实例
    id_generator = QuestionIDGenerator()

    # 导出常用变量
    es = es_client
    client = redis_client
    index_name = settings.ES_CONFIG['INDEX_NAME']
    rename_map = settings.FIELD_MAPPINGS
    allowed_fields = set(settings.ALLOWED_FIELDS)
    get_question_id = id_generator.generate

except Exception as e:
    logger.critical(f"系统初始化失败: {str(e)}")
    raise