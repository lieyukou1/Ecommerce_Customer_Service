from __future__ import annotations

from fastapi import FastAPI

from app.api import router


openapi_tags = [
    {
        "name": "系统",
        "description": "物业中台服务可用性与基础检查接口。",
    },
    {
        "name": "住户",
        "description": "查询住户关联工单与服务项目的接口。",
    },
    {
        "name": "工单",
        "description": "工单详情、状态、进度，以及投诉和催办相关接口。",
    },
    {
        "name": "服务项目",
        "description": "服务项目详情查询接口。",
    },
    {
        "name": "交互壳",
        "description": "保留单页交互壳的占位聊天接口。",
    },
]


app = FastAPI(
    title="Property Service Demo Backend",
    version="0.1.0",
    description=(
        "A property management demo backend mapped from the teacher's ecommerce sample, "
        "providing resident work orders, service items, service progress, complaint and urge request APIs."
    ),
    openapi_tags=openapi_tags,
)

app.include_router(router)
