"""允许使用 python -m compress_reme 运行服务器"""

import uvicorn

def main():
    """启动服务器"""
    uvicorn.run("compress_reme.server.app:app", host="0.0.0.0", port=8788, reload=True)

if __name__ == "__main__":
    main()
