# -*- coding: utf-8 -*-
# 第 4 步：记忆管理（短期=上下文窗口 / 长期=向量库）—— 本项目最大亮点
# 用法：python memory_demo.py
# 首次运行会下载 BGE 中文模型（约 400MB），需 HF 镜像生效
import datetime
import chromadb
from sentence_transformers import SentenceTransformer

emb = SentenceTransformer("BAAI/bge-base-zh-v1.5")
client = chromadb.PersistentClient(path="./memory_db")
col = client.get_or_create_collection(name="long_term_memory")

def save_memory(content, kind="task_result"):
    """长期记忆写入：任务结论 / 用户偏好存向量库"""
    e = emb.encode([content], normalize_embeddings=True).tolist()
    col.add(ids=[f"m{col.count()}"], embeddings=e, documents=[content],
            metadatas=[{"kind": kind, "ts": datetime.datetime.now().isoformat()}])

def retrieve_memory(query, n=3):
    """长期记忆检索：任务前取回相关历史，注入 prompt"""
    q = emb.encode(["为这个句子生成表示以用于检索相关文章：" + query],
                   normalize_embeddings=True).tolist()
    res = col.query(query_embeddings=q, n_results=n)
    return res["documents"][0]

if __name__ == "__main__":
    # 首次运行写入记忆，之后每次运行直接检索演示（避免重复累积）
    if col.count() == 0:
        save_memory("用户偏好：求职意向是 AI Agent 应用开发工程师，目标城市成都/上海")
        save_memory("上次任务结论：秋招时间线应 9 月投递、10 月笔试、11 月面试")
        print("✅ 已写入 2 条长期记忆（首次运行）\n")

    mem = retrieve_memory("用户求职意向和城市偏好是什么？")
    print("🔍 检索到的长期记忆：")
    for m in mem:
        print("  -", m)
