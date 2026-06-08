from fastapi import FastAPI
from contextlib import asynccontextmanager

from atguigu.api.dependencies import init_dialogue_engine
from atguigu.api.router.chat_router import router

from atguigu.infrastructure.database import close_db_engine, init_db_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1.回调lifespan的时机：在服务一启动的时候会先来调用（初始化HTTP客户端、Redis客户端、MySQL数据库的连接池...）
    2.参数app以及类型必须要指定，因为底层FastAPI对资源做共享和传递
    3.yield: 让FASTAPI处理请求，等应用关闭,才执行close_db_engine
    :return:
    """
    init_db_engine()
    init_dialogue_engine()
    yield
    await close_db_engine()


app = FastAPI(description='物业服务管家', lifespan=lifespan)

app.include_router(router=router)
