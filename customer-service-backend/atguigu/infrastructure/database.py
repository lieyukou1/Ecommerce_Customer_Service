import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from atguigu.config.config import settings

engine: AsyncEngine | None = None
async_session: async_sessionmaker[AsyncSession]


def init_db_engine():
    """
    功能：初始化全局异步数据库引擎和 session 工厂。

    输入：
    - 无；从 `settings.database_url` 读取连接信息。

    输出：
    - 无返回值；写入模块级 `engine` 和 `async_session`。

    调用情况：
    - `api.app.lifespan()`

    副作用：
    - 会建立数据库引擎对象。
    """
    global engine, async_session
    engine = create_async_engine(url=settings.database_url, echo=True)

    # 统一用一个 session 工厂给 API 依赖层按请求创建异步会话。
    async_session = async_sessionmaker(engine, expire_on_commit=False)


async def close_db_engine():
    """
    功能：关闭全局数据库引擎。

    输入：
    - 无。

    输出：
    - 无返回值。

    调用情况：
    - `api.app.lifespan()` 关闭阶段。

    副作用：
    - 会释放数据库连接池资源。
    """
    await engine.dispose()


async def main():
    """
    功能：以脚本方式快速验证数据库连接是否可用。

    输入：
    - 无。

    输出：
    - 无返回值；会在控制台打印 `SELECT 1` 的结果。

    调用情况：
    - 仅手动执行当前文件时使用。

    副作用：
    - 会初始化数据库连接并执行测试 SQL。
    """
    init_db_engine()

    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        print(result.fetchone())

    await close_db_engine()


if __name__ == "__main__":
    asyncio.run(main())
