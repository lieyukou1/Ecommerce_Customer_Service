import uvicorn

from atguigu.config.config import settings


if __name__ == "__main__":
    """
    功能：以脚本方式直接启动 FastAPI 应用。

    输入：
    - 无；从 `settings` 读取 host 和 port。

    输出：
    - 无返回值；当前进程会启动 uvicorn 服务。

    调用情况：
    - 本地直接运行 `python atguigu/main.py` 时触发。

    副作用：
    - 会启动 Web 服务并占用配置端口。
    """
    uvicorn.run(app="api.app:app", host=settings.app_host, port=settings.app_port)
