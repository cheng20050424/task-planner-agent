# 智能任务规划 Agent（Task Planner Agent）

基于 DeepSeek 大模型的智能任务规划 Agent：输入一个目标，自动拆解为可执行子任务、按依赖调度执行、调用工具完成任务，并通过双层记忆实现跨会话的上下文连续性。

## 核心指标（真实测试结果）

| 指标 | 结果 | 测试规模 |
|---|---|---|
| 任务拆解准确率 | **97.2%**（105/108） | 20 个目标 |
| 工具调用成功率 | **100%**（63/63） | 63 次工具调用 |
| 记忆命中率 | **100%**（10/10） | 10 条长期记忆 |

## 架构

```
用户目标
   │
   ▼
① 记忆检索（ChromaDB 向量库）── 取回相关历史记忆
   │
   ▼
② LLM 任务规划（DeepSeek，强制 JSON）── 拆解为子任务
   │
   ▼
③ 状态机调度执行 ── 依赖检查 → 工具调用 / LLM 推理
   │
   ▼
④ 汇总报告（LLM 生成）
   │
   ▼
⑤ 写回记忆 ── 本次结论存为长期记忆，供下次任务复用
```

## 核心特性

- **LLM 任务规划**：Prompt 约束 + `response_format={"type":"json_object"}` 强制 JSON，把目标拆成 3–6 个可执行子任务
- **工具调用**：字典映射实现 Function Calling（`search_web` / `calculate` / `get_current_time`），`ast` 安全求值 + 全角转半角清洗，防御 LLM 输出不稳定
- **双层记忆**：短期上下文窗口 + 长期 ChromaDB 向量库（BGE 中文嵌入），跨会话记住用户偏好
- **服务化**：FastAPI 提供 API，Streamlit 前端可视化

## 快速开始

```bash
# 1. 创建并激活环境（Python 3.11）
conda create -n agent python=3.11 -y && conda activate agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API key
#    复制 .env.example 为 .env，填入你的 DeepSeek key

# 4. 运行
python main.py          # 端到端跑一个目标（检索→规划→执行→报告→记忆）
python eval.py          # 跑三个核心指标的测试
uvicorn app:app         # 启动 FastAPI 服务（http://localhost:8000）
```

## 项目结构

| 文件 | 职责 |
|---|---|
| `planner_demo.py` | 规划器：让 LLM 把目标拆成子任务 |
| `agent_demo.py` | 执行器：工具调用 + 任务状态机 |
| `memory_demo.py` | 记忆：ChromaDB 向量库 + BGE 嵌入 |
| `main.py` | 整合：检索→规划→执行→报告→保存 五步闭环 |
| `app.py` / `ui.py` | FastAPI 服务 + Streamlit 前端 |
| `eval.py` | 三指标测试脚本 |

## 技术栈

Python · DeepSeek · OpenAI SDK · ChromaDB · Sentence-Transformers（BGE）· FastAPI · Streamlit
