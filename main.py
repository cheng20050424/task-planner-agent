# -*- coding: utf-8 -*-
# 第 5 步：整合 planner + 执行器 + 记忆 → 完整 Agent
# 用法：python main.py
import json
from planner_demo import llm, plan
from agent_demo import execute_task
from memory_demo import retrieve_memory, save_memory

def run(goal):
    print(f"🎯 目标：{goal}\n")
    # 1) 长期记忆注入：先检索相关历史
    mem = retrieve_memory(goal)
    if mem:
        print("🧠 检索到历史记忆：", mem[0][:40], "……\n")
    # 2) 规划：把历史记忆拼进 prompt，实现「记忆增强的规划」
    tasks = plan(f"{goal}\n\n参考历史记忆：{mem}")["tasks"]
    # 3) 执行
    results = {}
    for t in sorted(tasks, key=lambda x: x["id"]):
        r = execute_task(t, results)
        results[t["id"]] = r
        out = str(r.get("output", r.get("reason")))
        print(f"  → 任务{t['id']} [{r['status']}]: {out[:40]}")
    # 4) 汇总报告
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user",
                   "content": f"目标：{goal}\n历史记忆：{mem}\n执行结果：{json.dumps(results, ensure_ascii=False)}\n写一份简洁的执行报告"}],
    )
    report = resp.choices[0].message.content
    # 5) 保存本次结论为长期记忆（截断，避免过长）
    save_memory(f"任务结论（{goal}）：{report[:200]}")
    print("\n📝 已保存本次结论到长期记忆")
    return report

if __name__ == "__main__":
    print(run("帮我规划一次 AI 方向秋招求职"))
