"""
Calculator MCP Server
A showcase MCP server exposing several calculator tools plus a small
in-memory "history" resource so you can see tools + resources working
together.
"""

import math
from mcp.server import MCPServer

mcp = MCPServer("Calculator")

_history: list[str] = []


def _log(expression: str, result: float) -> None:
    _history.append(f"{expression} = {result}")
    if len(_history) > 20:
        _history.pop(0)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    result = a + b
    _log(f"{a} + {b}", result)
    return result


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    result = a - b
    _log(f"{a} - {b}", result)
    return result


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    result = a * b
    _log(f"{a} * {b}", result)
    return result


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises an error if b is 0."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    result = a / b
    _log(f"{a} / {b}", result)
    return result


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the given exponent."""
    result = math.pow(base, exponent)
    _log(f"{base} ^ {exponent}", result)
    return result


@mcp.tool()
def square_root(x: float) -> float:
    """Return the square root of x. Raises an error if x is negative."""
    if x < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    result = math.sqrt(x)
    _log(f"sqrt({x})", result)
    return result


@mcp.tool()
def percentage(part: float, whole: float) -> float:
    """Return what percent 'part' is of 'whole'."""
    if whole == 0:
        raise ValueError("Cannot divide by zero.")
    result = (part / whole) * 100
    _log(f"{part} is what % of {whole}", result)
    return result


@mcp.resource("history://recent")
def recent_history() -> str:
    """Return the most recent calculations performed in this session."""
    if not _history:
        return "No calculations yet."
    return "\n".join(_history)


if __name__ == "__main__":
    mcp.run()
