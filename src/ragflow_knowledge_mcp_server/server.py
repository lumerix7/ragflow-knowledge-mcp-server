"""server.py: This file contains the server code for the MCP server."""

from typing import Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent

from .logger import get_logger
from .properties import MCPServerProperties, Dataset
from .ragflow import get_api
from .schema.exceptions import ToolError, ToolExecutionError, ToolNotFoundError
from .service import search_knowledge, get_knowledge_base, list_knowledge_bases


def serve(properties_path: str | None = None) -> None:
    log = get_logger()

    properties = MCPServerProperties()
    api = get_api()

    properties.load(properties_path)

    log.info(f"Load properties from {properties_path} successfully.")

    server = Server(properties.server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools
        Convert datasets to a list of Tool objects
        """

        tools = []

        for dataset_id, dataset in properties.datasets.items():
            if dataset.search_tool_enabled:
                # The basic schema and parameters for the tool
                tool_schema = {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": dataset.query_param_description,
                        },
                    },
                    "required": ["query"],
                }
                # Add knowledge_base_id parameter if enabled
                if dataset.id_param_enabled:
                    tool_schema["properties"]["knowledge_base_id"] = {
                        "type": "string",
                        "description": dataset.dataset_id_param_description,
                    }
                    tool_schema["required"].append("knowledge_base_id")
                # Common parameters
                tool_schema["properties"]["top_k"] = {
                    "type": "integer",
                    "description": dataset.top_k_param_description,
                }
                tool_schema["properties"]["semantic_weights"] = {
                    "type": "number",
                    "description": dataset.weights_param_description,
                }

                # Add timeout parameter if enabled
                if properties.timeout_param_enabled:
                    tool_schema["properties"]["timeout"] = {
                        "type": "integer",
                        "description": properties.timeout_param_description,
                    }

                # Create the tool with valid name and description
                # Valid values of property type: "array", "boolean", "integer", "null", "number", "object", "string".
                tools.append(Tool(
                    name=dataset.search_tool_name,
                    description=dataset.search_tool_description,
                    inputSchema=tool_schema,
                ))
        # End of for loop

        # Add list bases tool if enabled
        if properties.list_bases_enabled:
            tool_schema = {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": properties.list_bases_page_param_description,
                    },
                    "limit": {
                        "type": "integer",
                        "description": properties.list_bases_limit_param_description,
                    },
                },
            }

            if properties.timeout_param_enabled:
                tool_schema["properties"]["timeout"] = {
                    "type": "integer",
                    "description": properties.timeout_param_description,
                }

            tools.append(Tool(
                name=properties.list_bases_name,
                description=properties.list_bases_description,
                inputSchema=tool_schema,
            ))

        # Add base info getting tool if enabled
        if properties.get_base_enabled:
            tool_schema = {
                "type": "object",
                "properties": {
                    "knowledge_base_id": {
                        "type": "string",
                        "description": properties.get_base_param_description,
                    },
                },
                "required": ["knowledge_base_id"],
            }

            if properties.timeout_param_enabled:
                tool_schema["properties"]["timeout"] = {
                    "type": "integer",
                    "description": properties.timeout_param_description,
                }

            tools.append(Tool(
                name=properties.get_base_name,
                description=properties.get_base_description,
                inputSchema=tool_schema,
            ))

        log.info(f"List tools: {len(tools)}, {tools}.")

        return tools

    @server.call_tool()
    async def call_tool(name: str, args: dict) -> Sequence[TextContent]:
        """Call the tool with the given name and arguments

        Raises:
            ToolError: If any error occurs while calling the tool.
        """

        log.info(f"Calling tool {name} with args: {args}.")

        if not name or not name.strip():
            log.error("Invalid argument: tool name is missing.")
            raise ToolExecutionError(message="Invalid argument: tool name is missing", code=400)
        name = name.strip()

        # Find dataset by tool name
        dataset = None
        tool = None
        for dataset_id, ds in properties.datasets.items():
            if ds.search_tool_enabled and ds.search_tool_name and ds.search_tool_name == name:
                dataset = ds
                tool = "search_knowledge"
                break

        if not tool and properties.list_bases_enabled and properties.list_bases_name == name:
            tool = "list_knowledge_bases"
        if not tool and properties.get_base_enabled and properties.get_base_name == name:
            tool = "get_knowledge_base"

        match tool:
            case None:
                # Get a list of valid tool names (excluding disabled or blank ones)
                valid_tool_names = []

                # Add query tool names
                valid_tool_names.extend([
                    dataset.search_tool_name
                    for dataset in properties.datasets.values()
                    if dataset.search_tool_enabled and dataset.search_tool_name
                ])

                # Add list tool name
                if properties.list_bases_enabled:
                    valid_tool_names.append(properties.list_bases_name)

                # Add name of query base info tool
                if properties.get_base_enabled:
                    valid_tool_names.append(properties.get_base_name)

                log.error(f"Tool name: {name} not found, valid tool names are: {valid_tool_names}.")
                raise ToolNotFoundError(f"Tool {name} not found, available tools are {valid_tool_names}")

            case "search_knowledge":
                result = await call_search_knowledge(dataset=dataset, args=args)

            case "list_knowledge_bases":
                result = await call_list_knowledge_bases(args=args)

            case "get_knowledge_base":
                result = await call_get_knowledge_base(args=args)

            case _:
                log.error(f"Unsupported tool: {name}.")
                raise ToolError(message=f"Unsupported tool: {name}", code=501)

        return [
            result
        ]

    async def call_search_knowledge(dataset: Dataset, args: dict) -> TextContent:
        """Calls the searching knowledge tool with the given arguments.

        Raises:
            ToolError: If any error occurs while calling the tool.
        """

        log.info(f"Calling searching knowledge tool with args: {args}.")

        try:
            result = await search_knowledge(properties=properties, api=api, dataset=dataset, args=args)

            return TextContent(
                type="text",
                text=result.get_simple_text() if dataset.search_tool_result == "simple" \
                    else result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)
            )
        except ToolError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while calling tool service: {e}.\n{traceback.format_exc()}")
            raise ToolExecutionError(message=f"Error while calling tool service: {e}", code=500)

    async def call_list_knowledge_bases(args: dict) -> TextContent:
        """Calls the list knowledge bases tool with the given arguments.

        Raises:
            ToolError: If any error occurs while calling the tool.
        """

        log.info(f"Calling list knowledge bases tool with args: {args}.")

        try:
            result = await list_knowledge_bases(properties=properties, api=api, args=args)

            return TextContent(
                type="text",
                text=result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)
            )
        except ToolError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while calling tool service: {e}.\n{traceback.format_exc()}")
            raise ToolExecutionError(message=f"Error while calling tool service: {e}", code=500)

    async def call_get_knowledge_base(args: dict) -> TextContent:
        """Calls the get knowledge base tool with the given arguments.

        Raises:
            ToolError: If any error occurs while calling the tool.
        """

        log.info(f"Calling get knowledge base tool with args: {args}.")

        try:
            result = await get_knowledge_base(properties=properties, api=api, args=args)

            return TextContent(
                type="text",
                text=result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)
            )
        except ToolError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while calling tool service: {e}.\n{traceback.format_exc()}")
            raise ToolExecutionError(message=f"Error while calling tool service: {e}", code=500)

    # Start the server
    options = server.create_initialization_options()

    if properties.transport == "sse":
        log.info(f"Starting server with SSE transport on {properties.sse_bind_host}:{properties.sse_port}... "
                 f"debug = {properties.sse_debug_enabled}, transport endpoint = {properties.sse_transport_endpoint}.")

        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        import uvicorn

        # Define handler functions
        async def handle_sse(request):
            async with sse.connect_sse(
                    request.scope, request.receive, request._send
            ) as streams:
                await server.run(streams[0], streams[1], options)

        # Create an SSE transport at an endpoint
        sse = SseServerTransport(properties.sse_transport_endpoint)

        # Create Starlette routes for SSE and message handling
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]

        # Create and run Starlette app
        starlette_app = Starlette(debug=properties.sse_debug_enabled, routes=routes)
        uvicorn.run(starlette_app, host=properties.sse_bind_host, port=properties.sse_port)
    else:
        import os

        # Check for stdio, SIMP_LOGGER_LOG_CONSOLE_ENABLED must be set to False
        if os.getenv("SIMP_LOGGER_LOG_CONSOLE_ENABLED", "True").lower() != "false":
            log.error("SIMP_LOGGER_LOG_CONSOLE_ENABLED must be set to False to use stdio transport.")
            raise ToolError(message="SIMP_LOGGER_LOG_CONSOLE_ENABLED must be set to False to use stdio transport",
                            code=400)

        log.info(f"Starting server with stdio transport... "
                 f"debug = {properties.sse_debug_enabled}, transport endpoint = {properties.sse_transport_endpoint}.")

        from mcp import stdio_server

        async def run_stdio_server():
            async with stdio_server() as (read_stream, write_stream):
                await server.run(read_stream, write_stream, options)

        import asyncio

        asyncio.run(run_stdio_server())
