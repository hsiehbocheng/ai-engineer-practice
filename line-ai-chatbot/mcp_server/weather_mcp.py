import asyncio
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"{location} 出現七道彩虹"


async def main():
    await mcp.run_async(transport="http", port=9000)

if __name__ == "__main__":
    asyncio.run(main())