import asyncio
from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b + 10000

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b + 10000


async def main():
    await mcp.run_async(transport="http", host="127.0.0.1", port=7000)

if __name__ == "__main__":
    asyncio.run(main())