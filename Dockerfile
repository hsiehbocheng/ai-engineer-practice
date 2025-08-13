# 使用含 uv/uvx 的基底映像
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 非 root 運行更安全
RUN useradd -m appuser
USER appuser
WORKDIR /app

# 環境變數：BigGo 需要的憑證與設定
ENV BIGGO_MCP_SERVER_REGION="TW"
ENV BIGGO_MCP_SERVER_SERVER_TYPE="sse"
ENV UVICORN_HOST="0.0.0.0"
ENV UVICORN_PORT="9876"
ENV BIGGO_MCP_SERVER_SSE_PORT="9876"

# 這個指令會拉最新 BigGo MCP Server 並以 SSE 模式啟動
EXPOSE 9876
CMD ["uvx", "BigGo-MCP-Server@latest", "--host", "0.0.0.0", "--port", "9876"]