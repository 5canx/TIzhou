"""
搜索服务层
"""
import logging
from utils.elasticsearch_utils import ElasticsearchService
from elasticsearch.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务类"""

    def __init__(self):
        self.es_service = ElasticsearchService()

    def process_options(self, options):
        """
        处理选项，检测text是否是图片路径
        """
        image_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        processed = []
        for opt in options:
            new_opt = opt.copy()
            text = new_opt.get("text", "")
            if isinstance(text, str) and text.lower().startswith("image") and text.lower().endswith(image_exts):
                new_opt["is_image"] = True
                new_opt["image"] = text
                new_opt.pop("text", None)
            else:
                new_opt["is_image"] = False
            processed.append(new_opt)
        return processed

    def search_by_id(self, question_id):
        """根据ID搜索题目"""
        try:
            source = self.es_service.search_by_id(question_id)
            
            # 处理选项图片
            if "options" in source and isinstance(source["options"], list):
                source["options"] = self.process_options(source["options"])

            return source
        except NotFoundError:
            raise ValueError(f"题目 ID {question_id} 未找到")
        except Exception as e:
            logger.error(f"根据ID搜索失败: {str(e)}")
            raise

    def search_by_content(self, keyword, size=10, from_=0):
        """根据内容搜索题目"""
        try:
            result = self.es_service.search_by_content(keyword, size, from_)
            hits = result.get("hits", [])
            
            if not hits:
                return {"results": [], "total": 0}

            results = []
            for hit in hits:
                source = hit["_source"]
                if "answer" in source and source["answer"] is not None:
                    source["answer"] = str(source["answer"])

                # 处理选项图片
                if "options" in source and isinstance(source["options"], list):
                    source["options"] = self.process_options(source["options"])

                results.append(source)

            return {
                "results": results, 
                "total": result.get("total", {}).get("value", 0)
            }
        except Exception as e:
            logger.error(f"根据内容搜索失败: {str(e)}")
            raise

    def list_all_questions(self, size=100, from_=0):
        """列出所有题目"""
        try:
            result = self.es_service.list_all(size, from_)
            hits = result.get("hits", [])
            
            results = []
            for hit in hits:
                source = hit["_source"]
                if "answer" in source and source["answer"] is not None:
                    source["answer"] = str(source["answer"])

                # 处理选项图片
                if "options" in source and isinstance(source["options"], list):
                    source["options"] = self.process_options(source["options"])

                results.append(source)

            return {
                "results": results,
                "total": result.get("total", {}).get("value", 0)
            }
        except Exception as e:
            logger.error(f"列出所有题目失败: {str(e)}")
            raise 