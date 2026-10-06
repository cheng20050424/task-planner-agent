# -*- coding: utf-8 -*-
# 第 3 步：工具集 + 执行器（工具调用 + 任务状态机）
# 复用 planner_demo.py 里的 llm 和 plan，无需再填 key
# 用法：python agent_demo.py
import json, ast, datetime
from planner_demo import llm, plan

# ---------- 工具集（体现"工具调用"） ----------
def search_web(query):
    # 演示版占位；真实接入：pip install ddgs 后接 DuckDuckGo 免费搜索
    return f"[搜索结果] 关于「{query}」：找到 3 条相关信息（接入 ddgs 后返回真实内容）"

def calculate(expression):
    # 先清洗：把中文/全角标点转成半角，防御 LLM 混入中文标点
    full_to_half = {
        "，": ",", "、": ",", "。": ".", "（": "(", "）": ")",
        "＋": "+", "－": "-", "＊": "*", "×": "*", "／": "/", "÷": "/",
        "＝": "=", "％": "%",
    }
    expr = str(expression).translate(str.maketrans(full_to_half)).replace(" ", "")
    # ast 安全求值，防 eval 注入
    try:
        node = ast.parse(expr, mode="eval")
        return str(eval(compile(node, "<calc>", "eval"), {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误: {e}"

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

TOOLS = {"search_web": search_web, "calculate": calculate, "get_current_time": get_current_time}

# ---------- 任务状态机 + 执行 ----------
def execute_task(task, results):
    """执行单个子任务（按依赖顺序，前置任务必须已完成）"""
    deps = task.get("depends_on", [])
    if not all(d in results for d in deps):
        return {"status": "failed", "reason": "前置任务未完成"}
    tool = task.get("tool", "none")
    if tool and tool != "none":
        # 有工具 → 调用工具，把 $result_<id> 占位符替换为前置任务结果
        args = task.get("args", {})
        for k, v in list(args.items()):
            if isinstance(v, str) and v.startswith("$result_"):
                args[k] = results.get(int(v[8:]), "")
        try:
            out = TOOLS[tool](**args)
            return {"status": "done", "output": str(out)}
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    else:
        # 无工具 → 交给 LLM 推理
        resp = llm.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user",
                       "content": f"执行这个任务并给出结果：{task['desc']}\n前置任务结果：{results}"}],
        )
        return {"status": "done", "output": resp.choices[0].message.content}

def run_agent(goal):
    tasks = plan(goal)["tasks"]
    results = {}
    print(f"📋 拆解出 {len(tasks)} 个子任务：")
    for t in tasks:
        print(f"  [{t['id']}] {t['desc'][:32]}... (tool={t.get('tool','none')})")
    # 按 id 顺序执行（规划器已保证依赖 id 更小）
    for t in sorted(tasks, key=lambda x: x["id"]):
        r = execute_task(t, results)
        results[t["id"]] = r
        out = str(r.get("output", r.get("reason")))
        print(f"  → 任务{t['id']} [{r['status']}]: {out[:50]}")
    # 汇总报告
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user",
                   "content": f"目标：{goal}\n执行结果：{json.dumps(results, ensure_ascii=False)}\n写一份简洁的执行报告"}],
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    print(run_agent("帮我规划一次 AI 方向秋招求职"))
