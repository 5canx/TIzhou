"""
文件处理工具模块
"""
import json
import pandas as pd
import os
import shutil
import zipfile
import logging
from datetime import datetime
from django.conf import settings
from .database import id_generator

logger = logging.getLogger(__name__)


class FileHandler:
    """文件处理基类"""
    
    def __init__(self):
        self.rename_map = settings.FIELD_MAPPINGS
        self.allowed_fields = set(settings.ALLOWED_FIELDS)

    def validate_fields(self, fields):
        """验证字段"""
        illegal_fields = [field for field in fields if field not in self.allowed_fields and not field.startswith('options.')]
        if illegal_fields:
            raise ValueError(f"文件存在非法字段: {illegal_fields}")


class JSONHandler(FileHandler):
    """JSON文件处理器"""
    
    def process(self, uploaded_file):
        """处理JSON文件"""
        try:
            content = uploaded_file.read().decode("utf-8")
            raw_data = json.loads(content)
            data_list = []

            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            elif not isinstance(raw_data, list):
                raise ValueError("JSON 格式不正确")

            for item in raw_data:
                if isinstance(item, dict):
                    mapped_item = {self.rename_map.get(k, k): v for k, v in item.items()}
                    data_list.append(mapped_item)

            return data_list
        except Exception as e:
            logger.error(f"处理JSON文件失败: {str(e)}")
            raise


class ExcelHandler(FileHandler):
    """Excel文件处理器"""
    
    def process(self, uploaded_file):
        """处理Excel文件"""
        try:
            # 保存上传的Excel文件到临时路径
            temp_dir = './temp'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # 读取数据
            df = pd.read_excel(temp_path)
            df.columns = [self.rename_map.get(col, col) for col in df.columns]

            # 验证字段
            self.validate_fields(df.columns)

            # 准备保存图片目录
            today = datetime.now().strftime("%Y%m%d")
            tmp_img_dir = os.path.join(settings.BASE_DIR, "static", "images", today, "tmp")
            save_dir = os.path.join(settings.BASE_DIR, "static", "images", today)
            os.makedirs(save_dir, exist_ok=True)

            data_list = []

            # 遍历每一题
            for idx, row in df.iterrows():
                item = {}
                for col in df.columns:
                    if col.startswith("options."):
                        continue
                    val = row[col]
                    if pd.notna(val):
                        item[col] = str(val).strip()

                # 获取题目 ID
                question_id = int(id_generator.generate()) + 1
                item["question_id"] = question_id

                options = []
                for i in range(5):  # 最多支持 A-E
                    label = chr(65 + i)  # A, B, C, ...
                    key = f"options.{i}.text"
                    val = row.get(key)

                    if pd.notna(val):
                        val_str = str(val).strip()

                        # 判断是否形如 1_A、2_C 等（即数字_大写字母）
                        if "_" in val_str and val_str.split("_")[-1].isalpha():
                            img_filename = val_str + ".png"
                            src_img_path = os.path.join(tmp_img_dir, img_filename)
                            dst_img_filename = f"{question_id + 2}_{label}.png"
                            dst_img_path = os.path.join(save_dir, dst_img_filename)

                            if os.path.exists(src_img_path):
                                shutil.copy2(src_img_path, dst_img_path)
                                options.append({
                                    "text": "",
                                    "image": f"images/{today}/{dst_img_filename}",
                                    "is_image": True
                                })
                            else:
                                options.append({
                                    "text": val_str,
                                    "image": "",
                                    "is_image": False
                                })
                        else:
                            options.append({
                                "text": val_str,
                                "image": "",
                                "is_image": False
                            })

                if options:
                    item["options"] = options

                item["ingest_time"] = datetime.now().isoformat()
                data_list.append(item)

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return data_list
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e)}")
            raise


class ImageHandler:
    """图片文件处理器"""
    
    @staticmethod
    def process_zip(uploaded_file):
        """处理ZIP文件中的图片"""
        try:
            # 创建临时目录
            temp_dir = './temp_images'
            os.makedirs(temp_dir, exist_ok=True)
            
            # 保存上传的ZIP文件
            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # 解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 准备保存目录
            today = datetime.now().strftime("%Y%m%d")
            save_dir = os.path.join(settings.BASE_DIR, "static", "images", today, "tmp")
            os.makedirs(save_dir, exist_ok=True)

            # 移动图片文件
            moved_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(save_dir, file)
                        shutil.move(src_path, dst_path)
                        moved_files.append(file)

            # 清理临时文件
            shutil.rmtree(temp_dir)

            return {
                "success": True,
                "message": f"成功上传 {len(moved_files)} 个图片文件",
                "files": moved_files
            }
        except Exception as e:
            logger.error(f"处理ZIP文件失败: {str(e)}")
            raise


def get_file_handler(file_type):
    """获取文件处理器"""
    handlers = {
        'json': JSONHandler,
        'xlsx': ExcelHandler,
        'xls': ExcelHandler,
    }
    return handlers.get(file_type.lower())() 