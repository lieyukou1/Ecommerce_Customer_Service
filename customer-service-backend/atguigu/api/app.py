from contextlib import asynccontextmanager

from fastapi import FastAPI

from atguigu.api.dependencies import init_dialogue_engine
from atguigu.api.router.chat_router import router
from atguigu.infrastructure.database import close_db_engine, init_db_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    功能：管理 FastAPI 应用启动和关闭时的全局资源初始化。

    输入：
    - app: 当前 FastAPI 应用实例。

    输出：
    - 作为异步上下文管理器供 FastAPI 使用。

    调用情况：
    - FastAPI 应用启动/关闭生命周期回调。

    副作用：
    - 会初始化数据库引擎和对话引擎，并在应用关闭时释放数据库连接。
    """
    init_db_engine()
    init_dialogue_engine()
    yield
    await close_db_engine()


app = FastAPI(description="物业服务管家", lifespan=lifespan)
app.include_router(router=router)
