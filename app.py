import streamlit as st
import time
from utils.logger_handler import logger
from agent.react_agent import smart_agent

# 1. 页面配置
st.set_page_config(
    page_title="小王智游 - AI 智慧旅游助手",
    page_icon="🌟",
    layout="wide"
)

# 自定义 CSS 样式
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .thought-container { color: #666; font-style: italic; font-size: 0.9em; }
    </style>
""", unsafe_allow_html=True)

st.title("🌟 小王智游 (WangSmartTravel)")
st.caption("基于 ReAct 架构与动态提示词切换的智慧旅游规划专家")

# 2. 初始化 Session State (聊天记录与 Session ID)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{int(time.time())}"

# 3. 侧边栏：监控与设置
with st.sidebar:
    st.header("⚙️ 控制面板")
    st.info(f"当前会话 ID: {st.session_state.session_id}")

    if st.button("🧹 清空聊天记录"):
        st.session_state.messages = []
        st.success("记忆已重置")

    st.divider()
    st.markdown("### 🛠️ 已加载工具")
    st.write("\n✅ RAG 攻略检索\n\n"
             "✅ 实时天气查询\n\n"
             "✅ 结构化数据查询\n\n"
             "✅ 预算审计系统")

# 4. 展示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 用户输入与 Agent 响应
if prompt := st.chat_input("想去哪里玩？请告诉我目的地、天数和预算..."):

    # 展示用户消息
    st.session_state.messages.append({"role": "human", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)

    # 展示 Agent 响应
    with st.chat_message("assistant"):
        # 创建用于展示思考过程的容器
        status_placeholder = st.status("小王正在思考并查阅资料...", expanded=True)
        # 创建用于展示最终回答的容器
        answer_placeholder = st.empty()

        prev_text = ""
        full_response = ""

        # 调用你的执行引擎（生成器模式）
        # 注意：这里传入 session_id 以适配你的持久化记忆逻辑
        try:
            for chunk in smart_agent.execute(prompt, session_id=st.session_state.session_id):

                # 情况 A：处理思考过程
                if chunk["type"] == "thought":
                    status_placeholder.write(chunk["content"])

                # 情况 B：处理工具观察结果
                elif chunk["type"] == "observation":
                    status_placeholder.write(f"✅ {chunk['content']}")

                # 情况 C：处理最终回答（或者是报告）
                elif chunk["type"] == "final_answer":
                    # 一旦开始输出最终回答，可以自动收起思考过程
                    # status_placeholder.update(label="✅ 资料搜集完毕", state="complete", expanded=False)

                    # full_response = chunk["content"]
                    # # 实时渲染 Markdown
                    # answer_placeholder.markdown(full_response)
                    new_text = chunk["content"]

                    delta = new_text[len(prev_text):]

                    for char in delta:
                        full_response += char
                        answer_placeholder.markdown(full_response)
                        time.sleep(0.01)

                    prev_text = new_text

            # 任务彻底完成后，收起状态栏
            status_placeholder.update(label="规划建议已就绪", state="complete", expanded=False)

            # 将回复存入 session_state
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            logger.error(f"App 执行异常: {e}")