# -*- coding: utf-8 -*-
# 第 6 步：测试脚本 —— 量化三个指标（写进简历的数字就靠它）
# 用法：python eval.py
# 说明：会调用多次 DeepSeek API，跑完约 2-5 分钟，请耐心等待
from planner_demo import plan
from agent_demo import execute_task
from memory_demo import save_memory, retrieve_memory

# 测试用的 5 个目标（可自行增删）
GOALS = [
    "帮我规划一次 AI 方向秋招求职",
    "制定一份 Python 入门学习计划",
    "筹备一场校园技术分享会",
    "规划一个机器学习项目从立项到上线",
    "安排一次为期两天的成都旅行",
    "制定一个健身减脂计划",
    "帮我准备考研复习计划",
    "策划一次班级团建活动",
    "制定一个英语六级备考计划",
    "规划一个图像分类深度学习项目",
    "帮我安排下个月的财务预算",
    "制定一份全年读书计划",
    "筹备一次生日聚会",
    "规划一个开源项目的贡献流程",
    "制定一份半程马拉松训练计划",
    "帮我规划毕业论文的写作进度",
    "制定一个面试准备计划",
    "规划一次三亚五天家庭旅行",
    "帮我制定一份简历优化计划",
    "规划一个公众号内容运营方案",
]

# ============ 指标 1：任务拆解（人工判断合理性） ============
def eval_plan():
    print("\n" + "=" * 60)
    print("指标 1：任务拆解 —— 请人工判断每个任务是否合理可执行")
    print("=" * 60)
    total = 0
    for g in GOALS:
        tasks = plan(g)["tasks"]
        total += len(tasks)
        print(f"\n【目标】{g}")
        for t in tasks:
            print(f"  [{t['id']}] {t['desc'][:36]} | tool={t.get('tool','none')} | depends={t.get('depends_on',[])}")
    print(f"\n>>> 共拆出 {total} 个子任务。请数出「合理」的数量 N，"
          f"拆解准确率 = N / {total}")

# ============ 指标 2：工具调用成功率（自动统计） ============
def eval_tool():
    print("\n" + "=" * 60)
    print("指标 2：工具调用成功率（自动统计）")
    print("=" * 60)
    tool_total = tool_ok = 0
    for g in GOALS:
        tasks = plan(g)["tasks"]
        results = {}
        for t in sorted(tasks, key=lambda x: x["id"]):
            has_tool = t.get("tool") and t.get("tool") != "none"
            if has_tool:
                tool_total += 1
            r = execute_task(t, results)
            results[t["id"]] = r
            if has_tool and r["status"] == "done":
                tool_ok += 1
    rate = tool_ok / tool_total * 100 if tool_total else 0
    print(f"分配了工具的任务数：{tool_total}")
    print(f"工具成功调用数：{tool_ok}")
    print(f">>> 工具调用成功率 = {tool_ok}/{tool_total} = {rate:.1f}%")

# ============ 指标 3：记忆命中率（自动统计） ============
MEMORY_ITEMS = [
    "用户的求职意向是 AI Agent 应用开发工程师",
    "用户的目标城市是成都和上海",
    "用户专业是人工智能",
    "用户会用 Claude Code 进行开发",
    "用户参加过电子设计大赛",
    "用户的毕业时间是 2027 年 6 月",
    "用户喜欢使用 DeepSeek 大模型",
    "用户有 YOLOv8 目标检测项目经验",
    "用户通过了英语 CET-4",
    "用户擅长 Python 编程",
]

def eval_memory():
    print("\n" + "=" * 60)
    print("指标 3：记忆命中率（自动统计）")
    print("=" * 60)
    for m in MEMORY_ITEMS:
        save_memory(m, kind="eval")
    hit = 0
    for m in MEMORY_ITEMS:
        res = retrieve_memory(m, n=5)
        if any(m in r for r in res):
            hit += 1
        else:
            print(f"  未命中：{m}")
    print(f">>> 记忆命中率 = {hit}/{len(MEMORY_ITEMS)} = {hit/len(MEMORY_ITEMS)*100:.1f}%")

if __name__ == "__main__":
    eval_plan()
    eval_tool()
    eval_memory()
    print("\n✅ 测试完成，把上面三个指标的数字记下来发我。")
