#!/usr/bin/env python3
from __future__ import annotations

import uvicorn

from app.config import settings


def main():
    print("Starting property service demo backend...")
    print(f"Host: http://{settings.app_host}:{settings.app_port}")
    print(f"Docs: http://{settings.app_host}:{settings.app_port}/docs")

    uvicorn.run(
        "app.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
