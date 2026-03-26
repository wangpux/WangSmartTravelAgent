import os
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abspath
from utils.logger_handler import logger
from utils.config_handler import config_handler
from utils.file_handler import file_handler
from model.factory import chat_model, embedding_model


class VectorStoreService:
    def __init__(self):
        # 1. 加载配置
        self.rag_config = config_handler.load_config("rag")
        self.chroma_config = config_handler.load_config("chroma")
        self.md5_store = get_abspath(self.chroma_config.get("md5_store"))

        # 2. 初始化向量数据库连接
        self.vector_db = Chroma(
            collection_name=self.chroma_config.get("collection_name"),
            embedding_function=embedding_model,
            persist_directory=get_abspath(self.chroma_config.get("persist_path"))
        )
        logger.info(f"Chroma 数据库已连接，持久化路径: {self.chroma_config.get("persist_path")}")

        # 3. 初始化文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chroma_config.get("chunk_size"),
            chunk_overlap=self.chroma_config.get("chunk_overlap"),
            separators=self.chroma_config.get("separators"),
            length_function=len
        )
        logger.info("文本分割器已加载")


    def add_document(self, file_path):
        """
        处理单文件：加载 -> MD5去重 -> 切分 -> 入库
        """
        # 1. 校验与 MD5 计算 (由 file_handler 完成)
        if not file_handler.validate_file(file_path):
            return

        file_md5 = file_handler.calculate_md5(file_path)
        if not file_md5:
            return

        # 3. 去重校验
        if file_handler.check_md5(file_md5):
            logger.info(f"文件 {os.path.basename(file_path)} 已经处理过，跳过。")
            return

        # 4. 加载文档
        docs = file_handler.load_file(file_path)
        if not docs:
            return

        # 5. 文本切分
        split_docs = self.splitter.split_documents(docs)

        # 6. 存入向量库
        self.vector_db.add_documents(split_docs)
        logger.info(f"文件 {os.path.basename(file_path)} 已存入向量库，切分块数: {len(split_docs)}")

        # 7. MD5值存入MD5库
        file_handler.save_md5(file_md5)


    def get_retriever(self):
        """
        检索最相关的 K 个片段 [cite: 81, 88]
        """
        logger.info("正在检索相关文档...")
        return self.vector_db.as_retriever(search_kwargs={'k':self.chroma_config.get('top_k')})


# 实例化
vector_service = VectorStoreService()

if __name__ == '__main__':
    data_dir = r"C:/Users/HP/Desktop/pythonProject/Agent项目/data"

    for file in os.listdir(data_dir):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(data_dir, file)
            print(f"正在处理: {pdf_path}")

            vector_service.add_document(pdf_path)
    # vector_service.add_document('C:/Users/HP/Desktop/pythonProject/Agent项目/data/我是驴友-大理.pdf')
    # res = vector_service.get_retriever().invoke('春天')
    # for r in res:
    #     print(r.page_content)
    #     print("-"*50)