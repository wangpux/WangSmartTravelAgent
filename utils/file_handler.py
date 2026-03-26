import hashlib
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.logger_handler import logger
from utils.config_handler import config_handler
from utils.path_tool import get_abspath


class FileHandler:
    """
    文件处理器：负责文件的 MD5 计算、类型检查及内容加载
    """

    def __init__(self):
        self.allowed_extensions = config_handler.load_config("chroma").get("allowed_extensions")
        self.md5_store = get_abspath(config_handler.load_config("chroma").get("md5_store"))


    def calculate_md5(self, file_path):
        """
        计算文件的 MD5 值，用于文件去重和完整性校验
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            md5_val = hash_md5.hexdigest()
            logger.info(f"文件 MD5 计算完成: {os.path.basename(file_path)} -> {md5_val}")
            return md5_val
        except Exception as e:
            logger.error(f"计算 MD5 出错: {e}")
            return None

    def check_md5(self, md5_val):
        if not os.path.exists(self.md5_store):
            open(self.md5_store, 'w', encoding='utf-8').close()
            return False
        with open(self.md5_store, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if md5_val == line:
                    return True
            return False

    def save_md5(self, md5_val):
        with open(self.md5_store, 'a', encoding='utf-8') as f:
            f.write(md5_val + "\n")
        logger.info("MD5 已存入 md5_store")

    def validate_file(self, file_path):
        """
        确保文件后缀名在允许范围内
        """
        ext = os.path.splitext(file_path)[-1].lower()
        if ext in self.allowed_extensions:
            return True
        logger.warning(f"不支持的文件类型: {ext} (仅支持 {self.allowed_extensions})")
        return False

    def load_file(self, file_path):
        """
        根据后缀名自动选择加载器加载文件内容
        """
        if not self.validate_file(file_path):
            return None
        try:
            # 1. 检查物理文件是否存在且大小不为0
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                logger.warning(f"文件 {os.path.basename(file_path)} 为空或不存在，跳过入库。")
                return None
        except Exception as e:
            logger.error(f"检查文件状态时出错: {e}")
            return None

        ext = os.path.splitext(file_path)[-1].lower()
        try:
            if ext == '.pdf':
                logger.info(f"正在加载 PDF 文件: {file_path}")
                loader = PyPDFLoader(file_path)
            elif ext == '.txt':
                logger.info(f"正在加载 TXT 文件: {file_path}")
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                return None

            # 返回的是 List[Document] 对象
            documents = loader.load()
            if not documents or all(not doc.page_content.strip() for doc in documents):
                logger.warning(f"文件 {os.path.basename(file_path)} 解析内容为空，跳过。")
                return None
            logger.info(f"文件加载成功，包含 {len(documents)} 页/段内容")
            return documents
        except Exception as e:
            # exc_info为True会记录详细的报错堆栈，如果为False仅记录报错信息本身
            logger.error(f"加载文件 {file_path} 失败: {e}", exc_info= True)
            return None


# 实例化
file_handler = FileHandler()