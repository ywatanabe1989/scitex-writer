<!-- ---
!-- Timestamp: 2025-08-27 09:18:35
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/minimal-pip-project/docs/to_claude/FastMCP_official_testing.md
!-- --- -->

The FastMCP Client is a deterministic testing tool that gives you complete programmatic control over MCP server interactions. You call specific tools with exact arguments, verify responses, and test edge cases - making it ideal for unit testing your MCP servers.
​
In-Memory Testing
The FastMCP Client’s standout feature is in-memory testing. Instead of deploying your server or managing network connections, you pass your server instance directly to the client. This creates a zero-overhead connection that runs entirely in memory.
What makes this approach so powerful is that everything runs in the same Python process. You can set breakpoints anywhere - in your test code or inside your server handlers - and step through with your debugger. There’s no server startup scripts, no port management, no cleanup between tests. Tests execute instantly without network overhead.

Copy
from fastmcp import FastMCP, Client

# Create your server
server = FastMCP("WeatherServer")

@server.tool
def get_temperature(city: str) -> dict:
    """Get current temperature for a city"""
    temps = {"NYC": 72, "LA": 85, "Chicago": 68}
    return {"city": city, "temp": temps.get(city, 70)}

@server.resource("weather://forecast")
def get_forecast() -> dict:
    """Get 5-day forecast"""
    return {"days": 5, "conditions": "sunny"}

async def test_weather_operations():
    # Pass server directly - no deployment needed
    async with Client(server) as client:
        # Test tool execution
        result = await client.call_tool("get_temperature", {"city": "NYC"})
        assert result.data == {"city": "NYC", "temp": 72}
        
        # Test resource retrieval
        forecast = await client.read_resource("weather://forecast")
        assert forecast.contents[0].data == {"days": 5, "conditions": "sunny"}
The in-memory approach transforms MCP testing from a deployment challenge into standard unit testing. You focus on testing your server’s behavior, not wrestling with infrastructure.
​
Testing with Frameworks
The FastMCP Client works seamlessly with any Python testing framework. Whether you prefer pytest, unittest, or another framework, the pattern remains consistent: create a server, pass it to the client, and verify behavior.

Copy
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def weather_server():
    server = FastMCP("WeatherServer")
    
    @server.tool
    def get_temperature(city: str) -> dict:
        temps = {"NYC": 72, "LA": 85, "Chicago": 68}
        return {"city": city, "temp": temps.get(city, 70)}
    
    return server

@pytest.mark.asyncio
async def test_temperature_tool(weather_server):
    async with Client(weather_server) as client:
        result = await client.call_tool("get_temperature", {"city": "LA"})
        assert result.data == {"city": "LA", "temp": 85}

@pytest.mark.asyncio
async def test_unknown_city(weather_server):
    async with Client(weather_server) as client:
        result = await client.call_tool("get_temperature", {"city": "Paris"})
        assert result.data["temp"] == 70  # Default temperature
​
Mocking External Dependencies
FastMCP servers are standard Python objects, so you can mock external dependencies using your preferred mocking approach. Replace databases, APIs, or any external service with test doubles to keep your tests fast and deterministic.

Copy
from unittest.mock import AsyncMock

async def test_database_tool():
    server = FastMCP("DataServer")
    
    # Mock the database
    mock_db = AsyncMock()
    mock_db.fetch_users.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    
    @server.tool
    async def list_users() -> list:
        return await mock_db.fetch_users()
    
    async with Client(server) as client:
        result = await client.call_tool("list_users", {})
        assert len(result.data) == 2
        assert result.data[0]["name"] == "Alice"
        mock_db.fetch_users.assert_called_once()
​
Testing Deployed Servers
While in-memory testing covers most unit testing needs, you’ll occasionally need to test against a deployed server - to verify authentication, test network behavior, or validate deployments.
​
HTTP Transport Testing
When you need to test actual network behavior or verify a deployment, connect to your running server using its URL:

Copy
from fastmcp import Client

async def test_deployed_server():
    # Connect to a running server
    async with Client("http://localhost:8000/mcp/") as client:
        await client.ping()
        
        # Test with real network transport
        tools = await client.list_tools()
        assert len(tools) > 0
        
        result = await client.call_tool("greet", {"name": "World"})
        assert "Hello" in result.data
​
Testing Authentication
The FastMCP Client handles authentication transparently, making it easy to test secured servers:

Copy
async def test_authenticated_server():
    # Bearer token authentication
    async with Client(
        "https://api.example.com/mcp",
        headers={"Authorization": "Bearer test-token"}
    ) as client:
        await client.ping()
        tools = await client.list_tools()
        
    # OAuth flow (opens browser for authorization)
    async with Client("https://api.example.com/mcp", auth="oauth") as client:
        result = await client.call_tool("protected_tool", {})
        assert result.data is not None
​
Best Practices
Default to in-memory testing - It’s faster, more reliable, and easier to debug
Test behavior, not implementation - Call tools and verify responses rather than testing internals
Use framework fixtures - Create reusable server configurations for your test suite
Mock external dependencies - Keep tests fast and deterministic by mocking databases, APIs, etc.
Test error cases - Verify your server handles invalid inputs and edge cases properly
The FastMCP Client transforms MCP server testing from a deployment challenge into a straightforward unit testing task. With in-memory connections and deterministic control, you can build comprehensive test suites that run in milliseconds.
Project Configuration

<!-- EOF -->