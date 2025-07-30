"""
上传服务层
"""
import logging
from utils.file_handlers import get_file_handler, ImageHandler
from utils.elasticsearch_utils import ElasticsearchService

logger = logging.getLogger(__name__)


class UploadService:
    """上传服务类"""

    def __init__(self):
        self.es_service = ElasticsearchService()

    def upload_file(self, uploaded_file):
        """上传并处理文件"""
        try:
            # 获取文件扩展名
            file_name = uploaded_file.name
            file_extension = file_name.split('.')[-1].lower()
            
            # 获取对应的文件处理器
            handler = get_file_handler(file_extension)
            if not handler:
                raise ValueError(f"不支持的文件类型: {file_extension}")

            # 处理文件
            data_list = handler.process(uploaded_file)
            
            # 批量索引到ES
            success, failed = self.es_service.bulk_index(data_list)
            
            return {
                "success": True,
                "message": f"成功上传 {len(data_list)} 条记录，索引成功 {success} 条，失败 {failed} 条",
                "total": len(data_list),
                "indexed": success,
                "failed": failed
            }
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise

    def upload_images(self, uploaded_file):
        """上传图片文件"""
        try:
            result = ImageHandler.process_zip(uploaded_file)
            return result
        except Exception as e:
            logger.error(f"图片上传失败: {str(e)}")
            raise 