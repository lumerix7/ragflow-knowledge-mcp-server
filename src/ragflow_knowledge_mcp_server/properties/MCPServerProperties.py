"""MCPServerProperties.py: This file contains the properties of the RAGFlow Knowledge API."""

from mcp import ErrorData, McpError
from yaml import YAMLError

from .Dataset import Dataset
from ..logger import get_logger
from ..utils import get_str_property, get_int_property, get_float_property, get_bool_property


class MCPServerProperties:
    """Properties for the RAGFlow Knowledge MCP server."""

    server_name: str = "RAGFlow Knowledge Base"

    # Transport type for MCP communication, default is stdio, available options are 'stdio', 'sse'.
    transport: str = "stdio"
    sse_transport_endpoint: str = "/messages/"
    sse_bind_host: str = "0.0.0.0"
    sse_port: int = 41106
    sse_debug_enabled: bool = True

    # Default base URL, default from environment variable DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL.
    default_base_url: str = None
    # Default API key, default from environment variable DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY.
    default_api_key: str = None

    # Total timeout of one calling for MCP tool, default is 60.0 seconds.
    timeout: float = 60.0
    # Whether to enable the MCP tool timeout parameter, default is False.
    timeout_param_enabled: bool = False
    # Description for total tool timeout parameter of one calling, default constructed based on timeout.
    #
    # NOTE: Parameter name always be 'timeout'.
    #
    timeout_param_description: str = None

    # Whether to enable the knowledge base listing MCP tool, default is False.
    list_bases_enabled: bool = False
    list_bases_name: str = "list_knowledge_bases"
    list_bases_description: str = "List knowledge bases."
    #
    # NOTE: Parameter names always be 'page' and 'limit'.
    #
    list_bases_page_param_description: str = "Page number to list the bases for, optional, defaults to 1."
    list_bases_limit_param_description: str = "Maximum number of knowledge bases to list, optional, defaults to 20."
    list_bases_base_url: str = None
    list_bases_api_key: str = None

    # Whether to enable the knowledge base(dataset) info getting MCP tool, default is False.
    get_base_enabled: bool = False
    # Name of the knowledge base getting MCP tool, default is get_knowledge_base_info.
    get_base_name: str = "get_knowledge_base_info"
    # Description of the knowledge base getting MCP tool.
    get_base_description: str = "Get information of the specified knowledge base ID, results including the knowledge base name, description, and other information."
    # Description for knowledge_base_id parameter, default is "Knowledge base ID to get info."
    #
    # NOTE: Parameter name always be 'knowledge_base_id'.
    #
    get_base_param_description: str = "Knowledge base ID to get info."

    # Dataset dict, key is dataset_id, value is Dataset object.
    #
    # NOTE: If id_param_enabled is True, the key or value.dataset_id should NOT be used as real dataset_id.
    #
    datasets: dict[str, Dataset] = {}

    def __init__(self):
        pass

    def load(self, properties_path: str = None):
        import os

        log = get_logger()

        # Check if properties_path is provided
        by_env_var = False
        if properties_path is None:
            default_path = "config.yaml" if os.path.exists("config.yaml") \
                else os.path.join(os.path.expanduser("~"), ".config", "ragflow-knowledge-mcp-server", "config.yaml")
            properties_path = os.getenv("RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG", default_path)
            if not properties_path:
                log.error("Properties path not found in environment variable RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG.")
                raise McpError(ErrorData(
                    code=404,
                    message="Properties path not found in environment variable RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG"))
            by_env_var = True
        # Check exists
        if not os.path.exists(properties_path):
            if by_env_var:
                log.error(f"Properties file {properties_path} does not exist, please set the environment variable "
                          f"RAGFLOW_KNOWLEDGE_MCP_SERVER_CONFIG to the path of the properties file.")
            else:
                log.error(f"Properties file {properties_path} does not exist.")
            raise McpError(ErrorData(code=404, message=f"Properties file {properties_path} does not exist"))

        log.info(f"Loading properties from {properties_path}.")

        # Read the properties from the yaml file
        try:
            import yaml

            with open(properties_path, 'r', encoding='utf-8') as file:
                properties = yaml.safe_load(file)

            # Extract properties from the loaded YAML
            if properties is None:
                log.warning(f"Properties file {properties_path} is empty.")
                return

            # Convert hyphen to underscore in keys
            properties_tmp = {}
            for k, v in properties.items():
                new_key = k.replace("-", "_") if isinstance(k, str) else k
                properties_tmp[new_key] = v
            properties = properties_tmp

            self._load_basic_properties(properties)
            self._load_list_bases_properties(properties)
            self._load_get_base_properties(properties)
            self._load_datasets(properties)

            # Check if datasets is empty
            if not self.datasets:
                log.error(f"No datasets found in properties file {properties_path}.")
                raise McpError(ErrorData(code=404, message=f"No datasets found in properties file {properties_path}"))

        except FileNotFoundError:
            log.error(f"Properties file not found: {properties_path}.")
            raise McpError(ErrorData(code=404, message=f"Properties file not found: {properties_path}"))
        except YAMLError as e:
            log.error(f"Error parsing YAML file: {e}.")
            raise McpError(ErrorData(code=400, message=f"Error parsing YAML file: {e}"))
        except Exception as e:
            if not isinstance(e, McpError):
                import traceback
                log.error(f"Error reading properties file: {e}.\n{traceback.format_exc()}")
                raise McpError(ErrorData(code=400, message=f"Error reading properties file: {e}"))
            raise e

    def _load_basic_properties(self, properties: dict):
        log = get_logger()

        name = get_str_property(props=properties, prop_name='server_name',
                                env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_NAME')
        if name:
            self.server_name = name.strip()
            log.info(f"Server name set to: {self.server_name}.")

        transport = get_str_property(props=properties, prop_name='transport',
                                     env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_TRANSPORT')
        if transport and transport in ['stdio', 'sse']:
            self.transport = transport.strip()
            log.info(f"Transport set to: {self.transport}.")

        if self.transport == 'sse':
            # SSE endpoint
            endpoint = get_str_property(props=properties, prop_name='sse_transport_endpoint',
                                        env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_TRANSPORT_ENDPOINT')
            if endpoint:
                self.sse_transport_endpoint = endpoint.strip()
                log.info(f"SSE transport endpoint set to: {self.sse_transport_endpoint}.")
            # SSE bind host
            host = get_str_property(props=properties, prop_name='sse_bind_host',
                                    env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_BIND_HOST')
            if host:
                self.sse_bind_host = host.strip()
                log.info(f"SSE bind host set to: {self.sse_bind_host}.")
            # SSE port
            port = get_int_property(props=properties, prop_name='sse_port',
                                    env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_PORT')
            if port is not None and 0 < port < 65536:
                self.sse_port = port
                log.info(f"SSE port set to: {self.sse_port}.")
            # SSE debug enabled
            debug_enabled = get_bool_property(props=properties, prop_name='sse_debug_enabled',
                                              env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_SSE_DEBUG_ENABLED')
            if debug_enabled is not None:
                self.sse_debug_enabled = debug_enabled
                log.info(f"SSE debug enabled set to: {self.sse_debug_enabled}.")

        default_base_url = get_str_property(props=properties, prop_name='default_base_url',
                                            env_var_name='DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL')
        if default_base_url:
            self.default_base_url = default_base_url.strip()
            log.info(f"Default base url set to: {self.default_base_url}.")

        default_api_key = get_str_property(props=properties, prop_name='default_api_key',
                                           env_var_name='DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY')
        if default_api_key and isinstance(default_api_key, str) and default_api_key.strip():
            self.default_api_key = default_api_key.strip()
            log.info(f"Default api key set to: {self.default_api_key}.")

        # Check tool timeout
        timeout = get_float_property(props=properties, prop_name='timeout',
                                     env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT')
        if timeout is not None and timeout >= 0.1:
            self.timeout = timeout
            log.info(f"Tool timeout set to: {self.timeout}.")
        # Check tool timeout parameter
        param_enabled = get_bool_property(props=properties, prop_name='timeout_param_enabled',
                                          env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT_PARAM_ENABLED')
        if param_enabled:
            self.timeout_param_enabled = True
            log.info(f"Tool timeout parameter enabled set to: {self.timeout_param_enabled}.")

            param_description = get_str_property(props=properties, prop_name='timeout_param_description',
                                                 env_var_name='RAGFLOW_KNOWLEDGE_MCP_SERVER_TIMEOUT_PARAM_DESCRIPTION')
            if param_description and isinstance(param_description, str) and param_description.strip():
                self.timeout_param_description = param_description.strip()
                log.info(f"Tool timeout parameter description set to: {self.timeout_param_description}.")
            else:
                self.timeout_param_description = f"Total timeout for one calling, in seconds, optional, defaults to {self.timeout} seconds."
        else:
            self.timeout_param_enabled = False

    def _load_list_bases_properties(self, properties: dict):
        log = get_logger()

        tool_enabled = get_bool_property(props=properties, prop_name='list_bases_enabled',
                                         default_value=self.list_bases_enabled)
        if not tool_enabled:
            log.info("List knowledge bases tool is disabled.")
            self.list_bases_enabled = False
            return

        tool_name = get_str_property(props=properties, prop_name='list_bases_name', default_value=self.list_bases_name)
        if not tool_name or not tool_name.strip():
            log.warning("List tool name is blank => not generate knowledge base list tool.")
            self.list_bases_enabled = False
            return

        tool_description = get_str_property(props=properties, prop_name='list_bases_description',
                                            default_value=self.list_bases_description)
        if not tool_description or not tool_description.strip():
            log.warning("List tool description is blank => not generate knowledge base list tool.")
            self.list_bases_enabled = False
            return

        page_param_description = get_str_property(props=properties, prop_name='list_bases_page_param_description',
                                                  default_value=self.list_bases_page_param_description)
        limit_param_description = get_str_property(props=properties, prop_name='list_bases_limit_param_description',
                                                   default_value=self.list_bases_limit_param_description)
        base_url = get_str_property(props=properties, prop_name='list_bases_base_url',
                                    default_value=self.list_bases_base_url)
        api_key = get_str_property(props=properties, prop_name='list_bases_api_key',
                                   default_value=self.list_bases_api_key)

        self.list_bases_enabled = True

        self.list_bases_name = tool_name.strip()
        self.list_bases_description = tool_description.strip()
        self.list_bases_page_param_description = page_param_description.strip()
        self.list_bases_limit_param_description = limit_param_description.strip()
        self.list_bases_base_url = base_url
        self.list_bases_api_key = api_key

        log.info(f"List knowledge bases tool enabled(list_bases_enabled) set to: {self.list_bases_enabled}.")
        log.info(f"List knowledge bases tool name(list_bases_name) set to: {self.list_bases_name}.")
        log.info(f"List knowledge bases tool description(list_bases_description) set to:"
                 f" {self.list_bases_description}.")
        log.info(f"List knowledge bases tool parameter description(list_bases_page_param_description) set to: "
                 f"{self.list_bases_page_param_description}.")
        log.info(f"List knowledge bases tool parameter description(list_bases_limit_param_description) set to: "
                 f"{self.list_bases_limit_param_description}.")
        log.info(f"List knowledge bases tool base url(list_bases_base_url) set to: {self.list_bases_base_url}.")
        log.info(f"List knowledge bases tool api key(list_bases_api_key) set to: {self.list_bases_api_key}.")

    def _load_get_base_properties(self, properties: dict):
        log = get_logger()

        tool_enabled = get_bool_property(props=properties,
                                         prop_name='get_base_enabled',
                                         default_value=self.get_base_enabled)
        if not tool_enabled:
            log.info("Knowledge base getting tool is disabled.")
            self.get_base_enabled = False
            return

        tool_name = get_str_property(props=properties, prop_name='get_base_name', default_value=self.get_base_name)
        if not tool_name or not tool_name.strip():
            log.warning("Knowledge base getting tool name is blank => not generate knowledge base getting tool.")
            self.get_base_enabled = False
            return

        tool_description = get_str_property(props=properties, prop_name='get_base_description',
                                            default_value=self.get_base_description)
        if not tool_description or not tool_description.strip():
            log.warning("Knowledge base getting tool description is blank => not generate knowledge base getting tool.")
            self.get_base_enabled = False
            return

        tool_param_description = get_str_property(props=properties, prop_name='get_base_param_description',
                                                  default_value=self.get_base_param_description)

        self.get_base_enabled = True

        self.get_base_name = tool_name.strip()
        self.get_base_description = tool_description.strip()
        self.get_base_param_description = tool_param_description.strip()

        log.info(f"Knowledge base getting tool enabled(get_base_enabled) set to: {self.get_base_enabled}.")
        log.info(f"Knowledge base getting tool name(get_base_name) set to: {self.get_base_name}.")
        log.info(f"Knowledge base getting tool description(get_base_description) set to: "
                 f"{self.get_base_description}.")
        log.info(f"Knowledge base getting tool parameter description(get_base_param_description) set to: "
                 f"{self.get_base_param_description}.")

    def _load_datasets(self, properties: dict):
        log = get_logger()

        datasets_list = properties.get('datasets', [])

        if datasets_list:
            seen_tool_names = {}

            for dataset_item in datasets_list:
                # Convert hyphen to underscore in keys
                # Create a new dictionary with converted keys instead of modifying during iteration
                dataset_properties = {}
                for k, v in dataset_item.items():
                    new_key = k.replace("-", "_") if isinstance(k, str) else k
                    dataset_properties[new_key] = v

                # Check whether the dataset is enabled
                enabled = get_bool_property(props=dataset_properties, prop_name='enabled', default_value=True)
                if not enabled:
                    log.warning(f"Dataset is disabled: {dataset_properties}.")
                    continue

                # Get dataset_id
                id_param_enabled = get_bool_property(props=dataset_properties,
                                                     prop_name='id_param_enabled',
                                                     default_value=False)
                if not id_param_enabled:
                    # Get dataset_id from the item
                    dataset_id = get_str_property(props=dataset_properties, prop_name='dataset_id', default_value=None)
                    # Check if dataset_id is blank
                    if not dataset_id or not dataset_id.strip():
                        log.warning("Dataset ID is blank => discarding this dataset.")
                        continue
                else:
                    dataset_id = f"__dataset_{len(self.datasets)}__"
                    log.info(f"id_param_enabled is True, dataset_id {dataset_id} should NOT be used as real "
                             f"dataset_id.")

                # Check for duplicates
                if dataset_id in self.datasets:
                    log.warning(f"Duplicate dataset ID found: {dataset_id} => using the latest definition.")

                log.debug(f"Dataset properties: {dataset_properties}.")

                dataset = Dataset(**dataset_properties)

                log.debug(f"Dataset: {dataset}.")

                # Check knowledge search tool
                if dataset.search_tool_enabled:
                    # Check whether search_tool_name is blank
                    if not dataset.search_tool_name or not dataset.search_tool_name.strip():
                        log.warning(f"search_tool_name is blank for {dataset_id} => not generate this knowledge search "
                                    f"tool.")
                        dataset.search_tool_enabled = False
                    # Discard duplicated tool names
                    if dataset.search_tool_name in seen_tool_names:
                        log.warning(f"Duplicate tool name found: {dataset.search_tool_name} => not generate this "
                                    f"knowledge search tool.")
                        dataset.search_tool_enabled = False
                    # Check whether search_tool_description is blank
                    if not dataset.search_tool_description or not dataset.search_tool_description.strip():
                        log.warning(f"search_tool_description is blank for {dataset_id} => not generate this knowledge "
                                    f"search tool.")
                        dataset.search_tool_enabled = False

                    # Check search_tool_result, default to 'json' if not provided or invalid
                    if not dataset.search_tool_result or dataset.search_tool_result not in ['json', 'simple']:
                        dataset.search_tool_result = 'json'
                        log.info(f"search_tool_result is not provided or invalid for {dataset_id} => set to 'json'.")

                    # Add search tool name to seen_tool_names if enabled
                    if dataset.search_tool_enabled:
                        dataset.search_tool_name = dataset.search_tool_name.strip()
                        dataset.search_tool_description = dataset.search_tool_description.strip()
                        seen_tool_names[dataset.search_tool_name] = True
                    else:
                        dataset.search_tool_name = ''
                        dataset.search_tool_description = ''

                if not dataset.search_tool_enabled:
                    log.warning(f"No tools are disabled for {dataset_id} => discarding this dataset.")
                    continue

                # Add/replace dataset in the map
                self.datasets[dataset_id] = dataset
                log.info(f"Loaded dataset properties for {dataset_id}: {dataset}.")
