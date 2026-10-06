# -*- coding: utf-8 -*-
# 第 5 步：FastAPI 后端服务
# 启动：uvicorn app:app --reload
from fastapi import FastAPI
from pydantic import BaseModel
from main import run

app = FastAPI(title="智能任务规划 Agent")

class Goal(BaseModel):
    goal: str

@app.post("/plan")
def plan_api(g: Goal):
    return {"report": run(g.goal)}

@app.get("/")
def index():
    return {"status": "ok", "message": "智能任务规划 Agent 后端已启动，POST /plan 传入 {goal}"}
