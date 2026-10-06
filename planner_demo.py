# -*- coding: utf-8 -*-
# 第 2 步：规划器 Planner —— 让 LLM 把目标拆成子任务
# 用法：复制 .env.example 为 .env，填入你的 DeepSeek key，然后运行：
#   python planner_demo.py
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

PLANNER_PROMPT = """你是任务规划器，把用户目标拆解为可执行的子任务。
规则：
1. 每个子任务具体、可执行、有明确产出；数量 3-6 个
2. 需要外部信息时指定 tool，工具签名如下（args 的键名必须严格一致）：
   - search_web：{"query": "搜索关键词"}
   - calculate：{"expression": "数学表达式，如 (10-3)*4"}
   - get_current_time：{}（无参数）
   - 无需工具：none，args 用 {}
3. 按依赖顺序排列，depends_on 填前置任务 id 数组（无依赖填 []）
4. 只输出 JSON，不要输出其它文字，格式：
{"tasks":[{"id":1,"desc":"...","tool":"none","args":{},"depends_on":[]}]}"""

def plan(goal):
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": goal},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)

if __name__ == "__main__":
    result = plan("帮我规划一次 AI 方向秋招求职")
    print(json.dumps(result, ensure_ascii=False, indent=2))
