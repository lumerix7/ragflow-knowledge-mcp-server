docker stop ragflow-knowledge-mcp-server
docker rm ragflow-knowledge-mcp-server

docker run -d --name ragflow-knowledge-mcp-server --privileged --restart unless-stopped -e SIMP_LOGGER_LOG_LEVEL=DEBUG -e RAGFLOW_KNOWLEDGE_MCP_SERVER_TRANSPORT=sse -e RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_DEBUG_ENABLED=True -e RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG="/root/config.yaml" -p 41106:41106 -v "%~dp0/config.yaml:/root/config.yaml" ragflow-knowledge-mcp-server:0.1.0
pause
