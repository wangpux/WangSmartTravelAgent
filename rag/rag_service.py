from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logger_handler import logger
from utils.prompt_handler import prompt_handler
from model.factory import chat_model
from rag.vector_store import vector_service


class RagSummarizeService:
    """
    RAG 总结服务：负责从向量库检索知识并生成专业解答
    """

    def __init__(self):
        # 1. 属性初始化
        self.vector_store = vector_service
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = prompt_handler.get_prompt("rag_summarize_prompt_path")
        self.model = chat_model
        self.chain = self._init_chain()
        logger.info("RagSummarizeService 初始化完成")

    def _init_chain(self):
        """
        构造 LangChain 流程：Prompt -> Model -> Parser
        """
        prompt_template = PromptTemplate.from_template(self.prompt_text)
        chain = prompt_template | self.model | StrOutputParser()
        return chain

    def rag_summarize(self, query):
        """
        执行完整的 RAG 总结流程
        """
        # 1. 检索相关文档
        logger.info(f"正在查询 '{query}' 的相关片段")
        docs = self.retriever.invoke(query)

        if not docs:
            logger.warning(f"查询 '{query}' 未检索到任何相关文档")
            return "抱歉，在现行资料库中未检索到相关信息。"

        # 2. 构造上下文 (将多个 Document 对象的 page_content 拼接)
        # 同时提取元数据（如文件名、页码）用于溯源
        context_list = []
        sources = set()
        for i, doc in enumerate(docs):
            content = doc.page_content.strip()
            source_name = doc.metadata.get("source", "未知出处")
            context_list.append(f"资料[{i + 1}] (来源: {source_name}):\n{content}")
            sources.add(source_name)

        full_context = "\n\n".join(context_list)

        # 3. 调用模型生成回答
        try:
            logger.info("正在调用模型生成总结...")
            response = self.chain.invoke({
                "context": full_context,
                "question": query
            })

            # 记录日志，方便后续调试 Agent 的观察结果
            logger.info(f"RAG 总结生成成功，参考来源: {list(sources)}")
            return response
        except Exception as e:
            logger.error(f"模型生成总结时出错: {e}")
            return "系统在处理知识总结时遇到了点问题，请稍后再试。"


# 实例化单例
rag_service = RagSummarizeService()

if __name__ == '__main__':
    print(rag_service.rag_summarize("三亚有什么特色"))