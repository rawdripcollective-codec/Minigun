from pathlib import Path

from fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent

mcp = FastMCP(
    name="Minigun FastMCP Server",
    instructions="Utility tools for exploring the Minigun repository.",
    version="1.0.0",
)


@mcp.tool(description="Echo back a message for connection testing.")
def echo(message: str) -> str:
    return message


@mcp.tool(description="Read the repository README for quick context.")
def read_readme() -> str:
    readme_path = BASE_DIR / "README.md"
    if not readme_path.exists():
        return "README.md not found."
    return readme_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
