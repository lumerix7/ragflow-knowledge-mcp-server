# ragflow-knowledge-mcp-server
A simple MCP server of knowledge base for RAGFlow.

**Supported RAGFlow versions:**

- 0.17.2



## 1. Available tools
### 1. Dynamic knowledge base searching tools
Enable dynamic knowledge base searching tools in `config.yaml`, see also [Server configurations](#3-server-configurations):

```yaml
datasets:
  - dataset-id: 00000000000000000000000000000000
    search-tool-name: search_xxx_knowledge
    #search-tool-description: "Search knowledge about XXX(中文说明)."
    #search-tool-result: simple
    search-tool-description: "Search knowledge about XXX(中文说明). Results in JSON format, knowledge in the 'content' property."
    search-tool-result: json
```


### 2. `list_knowledge_bases` (default disabled)
Enable `list_knowledge_bases` tool in `config.yaml`:

```yaml
list-bases-enabled: true
```

- **Default description:**
  List knowledge bases.

- **Input properties:**
  * `page`, str: The page number to list the bases for, optional, defaults to 1.
  * `limit`, str: The maximum number of knowledge bases to list, optional, defaults to 20.
  * `timeout`, int: Dynamic timeout parameter, enabled by `timeout-param-enabled`, optional, defaults to 60 seconds.


### 3. `get_knowledge_base_info` (default disabled)
Enable `get_knowledge_base_info` tool in `config.yaml`:

```yaml
get-base-enabled: true
```

- **Default description:**
  Get information of the specified knowledge base ID, results including the knowledge base name, description, and other information.

- **Input properties:**
  * `knowledge_base_id`, str: The ID of the knowledge base to query.
  * `timeout`, int: Dynamic timeout parameter, enabled by `timeout-param-enabled`, optional, defaults to 60 seconds.



## 2. Install and run
### 2.1. Install using pip
```bash
# Uninstall the previous version
pip uninstall --yes ragflow-knowledge-mcp-server

pip install ragflow-knowledge-mcp-server --upgrade --force-reinstall --extra-index-url http://127.0.0.1:8081/repository/pypi-group/simple --trusted-host 127.0.0.1
```


### 2.2. Install from source
```bash
cd /path/to/project

pip install .

# Or install using pytools.sh
./pytools.sh reinstall
```


### 2.3. Run
```bash
export SIMP_LOGGER_LOG_FILE=/path/to/mcp.log
export SIMP_LOGGER_LOG_LEVEL=DEBUG

# Run server directly
ragflow-knowledge-mcp-server --config=/path/to/config.yaml

# Or run with python
python -m ragflow_knowledge_mcp_server --config=/path/to/config.yaml

# Or run with uv
uv run ragflow-knowledge-mcp-server --config=/path/to/config.yaml
```


### 2.4. Run with Docker or Docker Compose
1. Docker

   * Export the `EXTRA_INDEX_URL` environment variable, then run [docker/0.1.0/build.sh](docker/0.1.0/build.sh) to build the image, modifying the build script as needed or building manually.
   * Then refer to [docker/0.1.0/run-in-docker.bat](docker/0.1.0/run-in-docker.bat) to run the container.

2. Docker Compose

   * Modify the `.env` file.
   * Modify the `config.yaml` file.
   * Run [docker/0.1.0/docker-compose-up-d.bat](docker/0.1.0/docker-compose-up-d.bat) to start the container, modifying the startup script as needed or running manually.



## 3. Server configurations
- **YAML**:

Example configurations `yaml`, for full configuration, see [MCPServerProperties.py](src/ragflow_knowledge_mcp_server/properties/MCPServerProperties.py):

```yaml
server-name: ragflow-knowledge-base

default-base-url: http://127.0.0.1:9388/api/v1
default-api-key: ragflow-00000000000000000000000000000000

timeout: 60
timeout-param-enabled: false

# SSE
transport: sse # Defaults to stdio
sse-port: 41106

list-bases-enabled: false
get-base-enabled: false

datasets:
  - dataset-id: 00000000000000000000000000000000
    search-tool-name: search_xxx_knowledge
    search-tool-description: "Search knowledge about XXX(中文说明). Results in JSON format, knowledge in the 'content' property."

  - enabled: false
    id-param-enabled: true
    search-tool-name: search_knowledge
    search-tool-description: "Search knowledge from specified knowledge base('knowledge_base_id')."
```

Or configures the base URL and API key for each dataset and tools:

```yaml
server-name: ragflow-knowledge-base

timeout: 60
timeout-param-enabled: false

# SSE
transport: sse # Defaults to stdio
sse-port: 41106

list-bases-enabled: false
list-bases-base-url: http://127.0.0.1:9388/api/v1
list-bases-api-key: ragflow-00000000000000000000000000000000

get-base-enabled: false

datasets:
  - dataset-id: 00000000000000000000000000000000
    base-url: http://127.0.0.1:9388/api/v1
    api-key: ragflow-00000000000000000000000000000000
    # Other properties...
```

- **Available environment variables**:

| Yaml                        | Environment variable name                                | Default value                                                                                  | Description                                                                         |
|-----------------------------|----------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
|                             | `RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG`                    | `config.yaml`                                                                                  | The config file path, also available in CLI option `--config=/path/to/config.yaml`. |
| `default-base-url`          | `DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL`                     | -                                                                                              | The default base URL for the knowledge base.                                        |
| `default-api-key`           | `DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY`                      | -                                                                                              | The default API key for the knowledge base.                                         |
| `server-name`               | `RAGFLOW_KNOWLEDGE_MCP_SERVER_NAME`                      | RAGFlow Knowledge Base                                                                         | The name of the MCP server.                                                         |
| `transport`                 | `RAGFLOW_KNOWLEDGE_MCP_SERVER_TRANSPORT`                 | stdio                                                                                          | The transport type. Can be `stdio` or `sse`.                                        |
| `sse-transport-endpoint`    | `RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_TRANSPORT_ENDPOINT`    | `/messages/`                                                                                   | The SSE transport endpoint.                                                         |
| `sse-bind-host`             | `RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_BIND_HOST`             | 0.0.0.0                                                                                        | The host to bind the SSE transport.                                                 |
| `sse-port`                  | `RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_PORT`                  | 41106                                                                                          | The port for the SSE transport.                                                     |
| `sse-debug-enabled`         | `RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_DEBUG_ENABLED`         | False                                                                                          | Whether to enable debug mode for SSE.                                               |
| `timeout`                   | `RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT`                   | 60                                                                                             | The timeout for the server.                                                         |
| `timeout-param-enabled`     | `RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT_PARAM_ENABLED`     | False                                                                                          | Whether to enable the timeout parameter.                                            |
| `timeout-param-description` | `RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT_PARAM_DESCRIPTION` | `The total timeout for one calling, in seconds, optional, defaults to {self.timeout} seconds.` | The description of the timeout parameter.                                           |



- **Available environment variables of `simp-logger`:**

| Variable name                       | Default value                                             | Description                                        |
|-------------------------------------|-----------------------------------------------------------|----------------------------------------------------|
| `SIMP_LOGGER_LOG_FILE_ENABLED`      | True                                                      | Whether to enable logging to file.                 |
| `SIMP_LOGGER_LOG_CONSOLE_ENABLED`   | True                                                      | Whether to enable logging to console.              |
| `SIMP_LOGGER_LOG_LEVEL`             | INFO                                                      | The log level.                                     |
| `SIMP_LOGGER_LOG_FILE`              | `~/logs/simp-logger.log`                                  | The log file path.                                 |
| `SIMP_LOGGER_LOG_PATTERN`           | `%(asctime)s %(levelname)s [%(threadName)s]: %(message)s` | The log pattern.                                   |
| `SIMP_LOGGER_LOG_MAX_BYTES`         | 10485760 (10MB)                                           | The maximum size of the log file.                  |
| `SIMP_LOGGER_LOG_BACKUP_COUNT`      | 5                                                         | The number of backup files to keep.                |
| `SIMP_LOGGER_LOG_ROTATION_TYPE`     | size                                                      | The type of log rotation. Can be `size` or `time`. |
| `SIMP_LOGGER_LOG_ROTATION_WHEN`     | midnight                                                  | The time of day to rotate the log file.            |
| `SIMP_LOGGER_LOG_ROTATION_INTERVAL` | 1                                                         | The interval for log rotation.                     |
| `SIMP_LOGGER_LOG_CLEANUP_DISABLED`  | False                                                     | Whether to disable logger cleanup.                 |



## 4. MCP configurations
### 4.1. SSE
Example endpoint: `http://127.0.0.1:41106/sse`


### 4.2. stdio
**⚠️ Note, for `stdio`, the `SIMP_LOGGER_LOG_CONSOLE_ENABLED` environment variable must be set to `false`.**`

Simple command line:

```bash
uv run ragflow-knowledge-mcp-server --config=/path/to/config.yaml
```

JSON:

```json
{
  "ragflow-knowledge-base": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "ragflow-knowledge-mcp-server",
      "--config=/path/to/config.yaml"
    ],
    "env": {
      "SIMP_LOGGER_LOG_CONSOLE_ENABLED": false,
      "SIMP_LOGGER_LOG_FILE": "/path/to/mcp.log",
      "SIMP_LOGGER_LOG_LEVEL": "DEBUG"
    }
  }
}
```

YAML:

```yaml
ragflow-knowledge-base:
  type: stdio
  command: uv
  args:
    - run
    - ragflow-knowledge-mcp-server
    - "--config=/path/to/config.yaml"
  env:
    SIMP_LOGGER_LOG_CONSOLE_ENABLED: false
    SIMP_LOGGER_LOG_FILE: /path/to/mcp.log
    SIMP_LOGGER_LOG_LEVEL: DEBUG
```
