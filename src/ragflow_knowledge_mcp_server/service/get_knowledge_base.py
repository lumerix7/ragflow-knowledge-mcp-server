"""services/get_knowledge_base.py"""

from ..logger import get_logger
from ..properties import MCPServerProperties
from ..ragflow import RAGFlowKnowledgeAPI, RAGFlowError
from ..schema import KnowledgeBase as GetKnowledgeBaseResult
from ..schema.exceptions import InvalidToolArgumentError, ToolAPIError


async def get_knowledge_base(properties: MCPServerProperties,
                             api: RAGFlowKnowledgeAPI,
                             args: dict,
                             ) -> GetKnowledgeBaseResult:
    """Retrieves the knowledge base information using the specified knowledge_base_id.

    Raises:
        - InvalidToolArgumentError: If the knowledge_base_id is invalid.
        - ToolAPIError:             If there is an error with the RAGFlow API.

    """

    log = get_logger()

    knowledge_base_id = args.get("knowledge_base_id", None)
    if not knowledge_base_id or not isinstance(knowledge_base_id, str) or not knowledge_base_id.strip():
        log.error(f"knowledge_base_id is required and should be a non-empty string. Got: {knowledge_base_id}.")
        raise InvalidToolArgumentError(
            f"knowledge_base_id is required and should be a non-empty string. Got: {knowledge_base_id}")

    # Find base_url and api_key by knowledge_base_id from properties
    # Note, if knowledge_base_id is not found in properties, it will be None, the default base_url and api_key will be used
    base_url = ''
    api_key = ''
    for dataset_id, ds in properties.datasets.items():
        if ds.dataset_id == knowledge_base_id:
            base_url = ds.base_url
            api_key = ds.api_key
            break
    if not base_url or not api_key:
        base_url = properties.default_base_url
        api_key = properties.default_api_key
        log.debug(f"Using default base_url: {base_url} and api_key: {api_key}.")

    timeout = properties.timeout
    if properties.timeout_param_enabled:
        t = args.get("timeout", properties.timeout)
        if t is not None and (not isinstance(t, (int, float)) or t < 0.1):
            log.error(f"timeout should be a positive number. Got: {t}.")
            raise InvalidToolArgumentError(f"timeout should be a positive number. Got: {t}")
        timeout = t

    try:
        base = await api.get_knowledge_base(
            dataset_id=knowledge_base_id,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )
    except RAGFlowError as e:
        log.error(f"Error while calling RAGFlow API: {e}.")
        raise ToolAPIError(message=f"Error while calling RAGFlow API: {e}", code=e.code)

    # Convert the base to GetKnowledgeBaseResult object
    from datetime import datetime

    indexing_technique = (
            " + ".join(
                label
                for label in (
                    base.parser_config.layout_recognize if base.parser_config else None,
                    "GraphRAG" if base.parser_config and base.parser_config.graphrag and base.parser_config.graphrag.get(
                        "use_graphrag", False) == True else None,
                    "RAPTOR" if base.parser_config and base.parser_config.raptor and base.parser_config.raptor.get(
                        "use_raptor", False) == True else None,
                )
                if label
            ) or None
    )

    result = GetKnowledgeBaseResult(
        knowledge_base_id=knowledge_base_id,
        name=base.name,
        description=base.description,
        provider=base.parser_config.layout_recognize if base.parser_config else None,
        permission=base.permission,
        indexing_technique=indexing_technique,
        document_count=base.document_count,
        word_count=base.token_num,
        created_by=base.created_by,
        created_at=datetime.fromtimestamp(
            base.create_time / 1000).isoformat() if base.create_time is not None else None,
        updated_at=datetime.fromtimestamp(
            base.update_time / 1000).isoformat() if base.update_time is not None else None,
    )

    log.debug(f"Retrieved knowledge base info:\n"
              f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
    return result
