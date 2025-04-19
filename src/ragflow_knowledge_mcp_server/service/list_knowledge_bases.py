"""services/list_knowledge_bases.py"""

from ..logger import get_logger
from ..properties import MCPServerProperties
from ..ragflow import RAGFlowKnowledgeAPI, RAGFlowError
from ..schema import KnowledgeBase
from ..schema.exceptions import InvalidToolArgumentError, ToolAPIError, DataError
from ..schema.list_knowledge_bases_types import ListKnowledgeBasesResult


async def list_knowledge_bases(properties: MCPServerProperties,
                               api: RAGFlowKnowledgeAPI,
                               args: dict,
                               ) -> ListKnowledgeBasesResult:
    """Retrieves a bases of knowledge base information.

    Raises:
        - InvalidToolArgumentError: If the page or limit is invalid.
        - ToolAPIError:             If there is an error with the RAGFlow API.
        - DataError:                If no knowledge bases are found.
    """

    log = get_logger()

    if properties.list_bases_base_url and properties.list_bases_api_key:
        base_url = properties.list_bases_base_url
        api_key = properties.list_bases_api_key
    else:
        base_url = properties.default_base_url
        api_key = properties.default_api_key

    page = args.get("page", 1)
    if page is not None and (not isinstance(page, int) or page < 1):
        log.error(f"page should be a positive integer. Got: {page}.")
        raise InvalidToolArgumentError(f"page should be a positive integer. Got: {page}")

    limit = args.get("limit", 20)
    if limit is not None and (not isinstance(limit, int) or limit < 1 or limit > 100):
        log.error(f"limit should be a positive integer between 1 and 100. Got: {limit}.")
        raise InvalidToolArgumentError(f"limit should be a positive integer between 1 and 100. Got: {limit}")

    timeout = properties.timeout
    if properties.timeout_param_enabled:
        t = args.get("timeout", properties.timeout)
        if t is not None and (not isinstance(t, int) or t < 1):
            log.error(f"timeout should be a positive integer. Got: {t}.")
            raise InvalidToolArgumentError(f"timeout should be a positive integer. Got: {t}")
        timeout = t

    try:
        bases = await api.list_knowledge_bases(
            base_url=base_url,
            api_key=api_key,
            page=page,
            limit=limit,
            timeout=timeout,
        )
    except RAGFlowError as e:
        log.error(f"Error while calling RAGFlow API: {e}.")
        raise ToolAPIError(message=f"Error while calling RAGFlow API: {e}", code=e.code)

    if not bases or not bases.data:
        log.error(f"No knowledge bases found for page: {page}, limit: {limit}.")
        raise DataError(message=f"No knowledge bases found for page: {page}, limit: {limit}.", code=404)

    # Convert the bases to ListKnowledgeBasesResult object
    from datetime import datetime

    result = ListKnowledgeBasesResult(
        data=[KnowledgeBase(
            knowledge_base_id=base.id,
            name=base.name,
            description=base.description,
            provider=base.parser_config.layout_recognize if base.parser_config else None,
            permission=base.permission,
            indexing_technique=(
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
            ,
            document_count=base.document_count,
            word_count=base.token_num,
            created_by=base.created_by,
            created_at=datetime.fromtimestamp(
                base.create_time / 1000).isoformat() if base.create_time is not None else None,
            updated_at=datetime.fromtimestamp(
                base.update_time / 1000).isoformat() if base.update_time is not None else None,
        ) for base in bases.data],
    )

    log.debug(f"Retrieved knowledge base info:\n"
              f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
    return result
