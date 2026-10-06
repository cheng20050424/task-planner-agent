# -*- coding: utf-8 -*-
# 第 5 步：Streamlit 前端
# 启动：streamlit run ui.py
import streamlit as st
import requests

st.set_page_config(page_title="智能任务规划 Agent", page_icon="🤖")
st.title("🤖 智能任务规划 Agent")
st.caption("输入一个目标，Agent 自动拆解 → 执行 → 记忆 → 出报告")

goal = st.text_input("输入你的目标", placeholder="例如：帮我规划一次 AI 方向秋招求职")

if st.button("开始规划", type="primary"):
    if not goal.strip():
        st.warning("请先输入目标")
    else:
        with st.spinner("Agent 正在规划中（约 10-30 秒）……"):
            try:
                r = requests.post("http://localhost:8000/plan",
                                  json={"goal": goal}, timeout=180)
                r.raise_for_status()
                st.success("✅ 规划完成")
                st.markdown(r.json()["report"])
            except Exception as e:
                st.error(f"请求失败：{e}")
