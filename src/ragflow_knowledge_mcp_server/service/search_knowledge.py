"""service/search_knowledge.py"""

from ..logger import get_logger
from ..properties import MCPServerProperties, Dataset
from ..ragflow import RAGFlowKnowledgeAPI, RAGFlowError
from ..schema.exceptions import InvalidToolArgumentError, ToolAPIError, DataError
from ..schema.search_knowledge_types import Knowledge, SearchKnowledgeResult


async def search_knowledge(properties: MCPServerProperties,
                           api: RAGFlowKnowledgeAPI,
                           dataset: Dataset,
                           args: dict,
                           ) -> SearchKnowledgeResult:
    """Queries the knowledge list using the specified dataset and searching args.

    Raises:
         - InvalidToolArgumentError: If the query, top_k, score_threshold_enabled, or score_threshold is invalid.
         - ToolAPIError:             If there is an error with the RAGFlow API.
         - DataError:                If no knowledge is found for the search.
    """

    log = get_logger()

    query = args.get("query", '')
    dataset_id = args.get("knowledge_base_id", None) if dataset.id_param_enabled else dataset.dataset_id
    top_k = args.get("top_k", dataset.default_top_k)
    score_threshold_enabled = args.get("score_threshold_enabled", dataset.default_score_threshold_enabled)
    score_threshold = args.get("score_threshold", dataset.default_score_threshold)

    if not query or not isinstance(query, str) or not query.strip():
        log.error(f"'query' is required and should be a non-empty string. Got: {query}.")
        raise InvalidToolArgumentError(f"'query' is required and should be a non-empty string. Got: {query}")

    if dataset.id_param_enabled and (not dataset_id or not isinstance(dataset_id, str) or not dataset_id.strip()):
        log.error(f"knowledge_base_id is required and should be a non-empty string. Got: {dataset_id}.")
        raise InvalidToolArgumentError(f"knowledge_base_id is required and should be a non-empty string. "
                                       f"Got: {dataset_id}")

    if not top_k or not isinstance(top_k, int) or top_k < 1:
        log.error(f"top_k should be a positive integer. Got: {top_k}.")
        raise InvalidToolArgumentError(f"top_k should be a positive integer. Got: {top_k}")

    if score_threshold_enabled is None or not isinstance(score_threshold_enabled, bool):
        log.error(f"score_threshold_enabled should be a boolean. Got: {score_threshold_enabled}.")
        raise InvalidToolArgumentError(f"score_threshold_enabled should be a boolean. Got: {score_threshold_enabled}")

    if score_threshold is not None and (not isinstance(score_threshold, float) or score_threshold < 0):
        log.error(f"score_threshold should be a non-negative float. Got: {score_threshold}.")
        raise InvalidToolArgumentError(f"score_threshold should be a non-negative float. Got: {score_threshold}")

    timeout = properties.timeout
    if properties.timeout_param_enabled:
        t = args.get("timeout", properties.timeout)
        if t is not None and (not isinstance(t, int) or t < 1):
            log.error(f"timeout should be a positive integer. Got: {t}.")
            raise InvalidToolArgumentError(f"timeout should be a positive integer. Got: {t}")
        timeout = t

    base_url = dataset.base_url
    api_key = dataset.api_key
    if not base_url or not api_key:
        base_url = properties.default_base_url
        api_key = properties.default_api_key
        log.debug(f"Using default base_url: {base_url} and api_key: {api_key}.")

    try:
        chunks = await api.retrieve_chunks(
            dataset_id=dataset_id,
            base_url=base_url,
            api_key=api_key,
            query=query,
            top_k=top_k,
            score_threshold_enabled=score_threshold_enabled,
            score_threshold=score_threshold,
            timeout=timeout,
        )
    except RAGFlowError as e:
        import traceback
        log.error(f"Error while calling RAGFlow API: {e}.\n{traceback.format_exc()}")
        raise ToolAPIError(message=f"Error while calling RAGFlow API: {e}", code=e.code)

    if not chunks or not chunks.data or not chunks.data.chunks or len(chunks.data.chunks) < 1:
        log.error(f"No knowledge chunks found for query: {query}.")
        raise DataError(message=f"No knowledge chunks found for query: {query}", code=404)

    # Convert the chunks to KnowledgeRecord objects if score, segment and segment.content are present
    knowledge_list = []
    for data in chunks.data.chunks:
        if data.similarity is None or data.content is None:
            log.warning(f"Record missing required fields: {data} => skipping.")
            continue

        knowledge = Knowledge(
            score=data.similarity,
            content=data.content
        )
        knowledge_list.append(knowledge)
    # Check if knowledge_list is empty
    if not knowledge_list:
        log.error(f"No knowledge found for query: {query}.")
        raise DataError(message=f"No knowledge found for query: {query}", code=404)

    # Sort the knowledge_list by score in descending order if score is present
    knowledge_list.sort(key=lambda x: x.score, reverse=True)
    # Only top k knowledge_list
    if len(knowledge_list) > top_k:
        log.warning(f"Knowledge list {len(knowledge_list)} exceeds top_k ({top_k}). Trimming to top_k.")
        knowledge_list = knowledge_list[:top_k]

    result = SearchKnowledgeResult(
        knowledge_list=knowledge_list,
        knowledge_base_id=dataset_id
    )

    log.debug(f"Retrieved {len(knowledge_list)} knowledge for query: {query} using dataset: {dataset_id}:\n"
              f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
    return result
