from langchain.agents import create_agent
from langchain_core.messages import AIMessage

from model.factory import chat_model
from utils.logger_handler import logger
from utils.prompt_handler import prompt_handler
from agent.tools.agent_tools import travel_tools
from agent.tools.middleware import travel_middlewares

class WangSmartTravelAgent:
    """
    小王智游 (SmartTravel) 核心 Agent：负责 ReAct 循环调度及提示词动态切换
    """

    def __init__(self):
        # 1. 加载基础组件
        self.model = chat_model
        self.tools = travel_tools
        self.middlewares = travel_middlewares

        # 2. 初始化主提示词
        self.main_prompt_text = prompt_handler.get_prompt("main_prompt_path")

        # 3. 创建核心执行引擎
        self.agent = create_agent(
            model= self.model,
            system_prompt= self.main_prompt_text,
            tools= self.tools,
            middleware= self.middlewares
        )

        self.session_histories = {}


    def execute(self, query: str, session_id: str = "default_user"):
        """
        执行用户请求：包含 ReAct 推理和报告模式检测
        """
        logger.info(f"--- [Agent 开始执行用户请求: {query}] ---")

        history = self.session_histories.get(session_id, [])
        agent_input = history + [{"role": "human", "content": query}]
        final_answer = ""

        # 1. 使用 stream 模式迭代执行
        try:
            for chunk in self.agent.stream(input={'messages': agent_input}, stream_mode="values", context= {"report": False}):
                # 2. 解析不同类型的 chunk

                # # create_agent 不返回 ReAct 中间步骤，不会有情况 A\B\C
                # # 情况 A：模型正在思考 (Thought) 或决定调用工具 (Action)
                # if "actions" in chunk:
                #     for action in chunk["actions"]:
                #         thought_log = f"Agent 思考中: {action.log}"
                #         logger.info(f"Agent 正在思考并决定调用工具: [{action.tool}] | 参数: {action.tool_input}")
                #         yield {"type": "thought", "content": thought_log}
                #
                # # 情况 B：工具执行完毕，返回结果 (Observation)
                # elif "steps" in chunk:
                #     for step in chunk["steps"]:
                #         obs_log = f"工具 [{step.action.tool}] 返回了相关数据..."
                #         logger.info(f"工具 [{step.action.tool}] 返回结果，长度: {len(str(step.observation))}")
                #
                #         if step.action.tool == "generate_report_signal":
                #             logger.info("状态变更：下一轮推理将自动切换至 [报告专家提示词]")
                #
                #         yield {"type": "observation", "content": obs_log}
                #
                # # 情况 C：最终结果输出 (Final Answer)
                # elif "output" in chunk:
                #     final_answer = chunk["output"]
                #     logger.info("最终方案生成完毕")
                #     yield {"type": "final_answer", "content": final_answer}
                #
                # # D：【新增调试】捕获原始消息（如果 Executor 内部解析失败，内容会留在这里）
                # elif "messages" in chunk:
                #     msg = chunk["messages"][-1]
                #     if hasattr(msg, "content") and msg.content:
                #         yield {"type": "final_answer", "content": msg.content}
                if "messages" in chunk:
                    msg = chunk["messages"][-1]

                    if isinstance(msg, AIMessage) and msg.content:
                        final_answer = msg.content
                        yield {"type": "final_answer", "content": msg.content}

            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": final_answer})
            logger.info(f"当前会话历史：{history}")

            self.session_histories[session_id] = history

        except Exception as e:
            error_msg = f"Agent 执行流异常: {str(e)}"
            logger.error(error_msg)
            yield {"type": "error", "content": error_msg}

# 实例化
smart_agent = WangSmartTravelAgent()

if __name__ == "__main__":
    # 模拟一次带报告需求的测试
    q1 = "我想去拉萨玩3天，预算5000元够吗？"
    # 调用执行
    print("\n--- 任务开始 ---")
    res1 = smart_agent.execute(q1, session_id="wang_001")
    print("\n--- 最终输出 ---")
    for item in res1:
        print(item['content'])
    print("\n--- 第二轮执行 (测试记忆) ---")
    q2 = "帮我生成一份详细的攻略报告。"
    for item in smart_agent.execute(q2, session_id="wang_001"):
        print(item['content'])
