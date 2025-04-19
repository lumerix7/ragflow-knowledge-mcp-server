"""properties/Dataset.py"""

from pydantic import BaseModel


class Dataset(BaseModel):
    """Dataset(i.e. Knowledge base) properties."""

    # Whether to enable this dataset, default is True.
    enabled: bool = True

    # The ID of the dataset, default is None.
    # If id_param_enabled is False, this parameter is required, otherwise it will be ignored.
    dataset_id: str = None
    # Whether to enable the 'knowledge_base_id' parameter, default is False.
    #
    # NOTE: The parameter name always be "knowledge_base_id".
    #
    id_param_enabled: bool = False
    # The description of dataset_id parameter.
    dataset_id_param_description: str = "The ID of the knowledge base to retrieve the knowledge list from, required."

    # Whether to enable searching MCP tool for this dataset, default is True.
    search_tool_enabled: bool = True
    # The name of the dataset for searching MCP tool.
    search_tool_name: str
    # The description of knowledge searching MCP tool.
    # Example:
    #    Search knowledge list about the XXX-English(中文说明)
    search_tool_description: str = None
    # The result format of the searching tool, default is 'json', available formats are 'json' and 'simple'.
    search_tool_result: str = "json"

    query_param_description: str = "The question or keywords to retrieve the knowledge from the knowledge base, required."
    top_k_param_description: str = "The maximum number of knowledge list to retrieve, optional, defaults to 3."
    weights_param_description: str = "The Semantic search weight in hybrid_search mode, optional, defaults to 0.6."
    score_threshold_enabled_param_description: str = "Whether to enable score threshold, optional, defaults to False."
    score_threshold_param_description: str = "The score threshold value, optional, defaults to 0.5, used when score_threshold_enabled is True."

    # The base URL for the API, default is None, use the default API URL.
    base_url: str = None
    # All API requests should include your API-Key in the Authorization HTTP Header, as shown below:
    # Authorization: Bearer {API_KEY}
    # Default is None, use the default API key.
    api_key: str = None

    default_top_k: int = 3
    default_weights: float = 0.6
    default_score_threshold_enabled: bool = False
    default_score_threshold: float = 0.5
