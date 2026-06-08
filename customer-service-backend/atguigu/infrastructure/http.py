import asyncio

from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client():
    """
    功能：初始化全局 HTTP 客户端。

    输入：
    - 无。

    输出：
    - 无返回值；写入模块级 `http_client`。

    调用情况：
    - 当前项目暂未在主链统一接入，主要用于独立调试。

    副作用：
    - 会创建全局 HTTP 客户端实例。
    """
    global http_client
    http_client = AsyncClient(timeout=10.0)


async def close_http_client():
    """
    功能：关闭全局 HTTP 客户端。

    输入：
    - 无。

    输出：
    - 无返回值。

    调用情况：
    - 手动调试脚本收尾。

    副作用：
    - 会释放 HTTP 连接资源。
    """
    await http_client.aclose()


async def main():
    """
    功能：以脚本方式验证中台 HTTP 请求是否可达。

    输入：
    - 无。

    输出：
    - 无返回值；会打印示例工单数据。

    调用情况：
    - 仅手动执行当前文件时使用。

    副作用：
    - 会发起真实 HTTP 请求。
    """
    init_http_client()

    response = await http_client.get(url="http://192.168.200.145:18081/residents/r1001/work-orders")
    print(response.json()["data"]["work_orders"])


if __name__ == "__main__":
    asyncio.run(main())
