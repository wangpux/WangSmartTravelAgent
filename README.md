# 🌟 小王智游 WangSmartTravel Agent

一个基于 **ReAct 架构 + LangChain + Streamlit** 的智能旅游规划助手。

## 🚀 项目亮点

- 🧠 基于 ReAct 推理的 Agent 决策系统
- 🔧 多工具调用（天气 / 预算 / RAG 攻略）
- 💬 多轮对话记忆（Session-based Memory）
- 📊 流式输出（类 ChatGPT 体验）
- 📄 自动生成结构化旅行报告

## 🏗️ 技术栈

- LangChain / Agent
- Streamlit（前端）
- Python
- RAG（PDF 检索）
- 多工具调用（Tool Calling）

## 🎯 功能演示

### 1️⃣ 普通咨询
> “三亚3天预算5000够吗？”

👉 预算评估 + 输出推荐

---

### 2️⃣ 规划任务
> “三亚怎么深度游玩？”

👉 自动调用：
- 天气 API
- 预算计算
- 攻略检索

---

### 3️⃣ 报告生成
> “帮我生成详细攻略报告”

👉 输出完整旅行计划（含行程）

---

## 📦 安装

```bash
pip install -r requirements.txt