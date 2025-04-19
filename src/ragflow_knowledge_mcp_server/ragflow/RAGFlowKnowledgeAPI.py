"""RAGFlowKnowledgeAPI.py"""

import asyncio
import json
import os
import os.path
from typing import Dict

from . import RAGFlowError
from .list_knowledge_bases_types import ListKnowledgeBasesResult, KnowledgeBase as GetKnowledgeBaseResult
from .retrieve_chunks_types import RetrieveChunksResult
from ..logger import get_logger

_ragflow_code_dict = {
    0: 200,
    100: 404,
    102: 404,
    109: 401,
}


class RAGFlowKnowledgeAPI:
    _apis: Dict[str, 'RAGFlowKnowledgeAPI'] = {}

    # The default base API URL
    default_base_url: str
    # All API requests should include your API-Key in the Authorization HTTP Header, as shown below:
    # Authorization: Bearer {API_KEY}
    default_api_key: str

    def __init__(self, default_base_url: str = None, default_api_key: str = None):
        """Constructs a RAGFlowKnowledgeAPI.

        Args:
            :param default_base_url: (str, optional): The default base URL for the API.
                                                      If not provided or invalid, the base URL will be loaded from the environment variable DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL.
            :param default_api_key: (str, optional):  The API key for authentication.
                                                      If not provided or invalid, the API key will be loaded from the environment variable DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY.
        """

        log = get_logger()

        if default_base_url and default_base_url.strip():
            self.default_base_url = default_base_url
        else:
            self.default_base_url = os.getenv("DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL")
            if not self.default_base_url or not self.default_base_url.strip():
                self.default_base_url = ''
                log.warning("Default base URL not found in environment variable DEFAULT_RAGFLOW_KNOWLEDGE_BASE_URL.")

        if default_api_key and default_api_key.strip():
            self.default_api_key = default_api_key
        else:
            self.default_api_key = os.getenv("DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY")
            if not self.default_api_key or not self.default_api_key.strip():
                self.default_api_key = ''
                log.warning("Default API key not found in environment variable DEFAULT_RAGFLOW_KNOWLEDGE_API_KEY.")

    @classmethod
    def get_api(cls,
                name: str = 'default',
                default_base_url: str = None,
                default_api_key: str = None,
                ) -> 'RAGFlowKnowledgeAPI':
        """Get the RAGFlowKnowledgeAPI instance.

        Args:
            :param name: (str, optional):             The name of the API instance.
            :param default_base_url: (str, optional): The default base URL for the API.
            :param default_api_key: (str, optional):  The default API key for authentication.

        Returns:
            RAGFlowKnowledgeAPI instance.
        """

        api = cls._apis.get(name, None)
        if not api:
            api = RAGFlowKnowledgeAPI(default_base_url=default_base_url, default_api_key=default_api_key)
            cls._apis[name] = api

        return api

    async def retrieve_chunks(self,
                              dataset_id: str,
                              query: str,
                              base_url: str = None,
                              api_key: str = None,
                              top_k: int = 3,
                              vector_chunk_size: int | None = None,
                              weights: float = 0.6,
                              score_threshold_enabled: bool = False,
                              score_threshold: float = 0.5,
                              timeout: int | None = None,
                              ) -> RetrieveChunksResult:
        """Retrieves Chunks from a Knowledge Base.

        - API: POST /api/v1/retrieval

        - Request Body
            "question": (Body parameter), string, Required
            The user query or query keywords.
            "dataset_ids": (Body parameter) list[string]
            The IDs of the datasets to search. If you do not set this argument, ensure that you set "document_ids".
            "document_ids": (Body parameter), list[string]
            The IDs of the documents to search. Ensure that all selected documents use the same embedding model. Otherwise, an error will occur. If you do not set this argument, ensure that you set "dataset_ids".
            "page": (Body parameter), integer
            Specifies the page on which the chunks will be displayed. Defaults to 1.
            "page_size": (Body parameter)
            The maximum number of chunks on each page. Defaults to 30.
            "similarity_threshold": (Body parameter)
            The minimum similarity score. Defaults to 0.2.
            "vector_similarity_weight": (Body parameter), float
            The weight of vector cosine similarity. Defaults to 0.3. If x represents the weight of vector cosine similarity, then (1 - x) is the term similarity weight.
            "top_k": (Body parameter), integer
            The number of chunks engaged in vector cosine computation. Defaults to 1024.
            "rerank_id": (Body parameter), integer
            The ID of the rerank model.
            "keyword": (Body parameter), boolean
            Indicates whether to enable keyword-based matching:
                true: Enable keyword-based matching.
                false: Disable keyword-based matching (default).
            "highlight": (Body parameter), boolean
            Specifies whether to enable highlighting of matched terms in the results:
                true: Enable highlighting of matched terms.
                false: Disable highlighting of matched terms (default).

            | Name                          | Type   | Default | Description                                                | Required |
            |-------------------------------|--------|---------|------------------------------------------------------------|----------|
            | question                      | string |         | The user query or query keywords.                          | Yes      |
            | dataset_ids                   | list   |         | The IDs of the datasets to search. If you do not set this argument, ensure that you set "document_ids". | No |
            | document_ids                  | list   |         | The IDs of the documents to search. Ensure that all selected documents use the same embedding model. Otherwise, an error will occur. If you do not set this argument, ensure that you set "dataset_ids". | No |
            | page                          | int    | 1       | Specifies the page on which the chunks will be displayed.  | No       |
            | page_size                     | int    | 30      | The maximum number of chunks on each page.                 | No       |
            | similarity_threshold          | float  | 0.2     | The minimum similarity score. Defaults to 0.2.             | No       |
            | vector_similarity_weight      | float  | 0.3     | The weight of vector cosine similarity. If x represents the weight of vector cosine similarity, then (1 - x) is the term similarity weight. | No |
            | top_k                         | int    | 1024?   | The number of chunks engaged in vector cosine computation. | No       |
            | rerank_id                     | int?   |         | The ID of the rerank model (v0.17.2, not work).            | No       |
            | keyword                       | bool   | false   | Indicates whether to enable keyword-based matching: true: Enable keyword-based matching. false: Disable keyword-based matching. | No |
            | highlight                     | bool   | false   | Specifies whether to enable highlighting of matched terms in the results: true: Enable highlighting of matched terms. false: Disable highlighting of matched terms. | No |


        - Response: RetrieveChunksResult, see retrieve_chunks_types.py for details.

        Args:
            :param dataset_id:              Knowledge ID.
            :param query:                   Query keyword.
            :param base_url:                Base URL, default is None to use the default base URL
            :param api_key:                 API key, default is None to use the default API key
            :param top_k:                   Number of results to return, default is 3.
            :param vector_chunk_size:       Chunk size for vector search, default is None. If None, it will be set to max(2, 1 << ((top_k - 1).bit_length())).
            :param weights:                 Semantic search weight setting in hybrid search mode, default is 0.6.
            :param score_threshold_enabled: Whether to enable score threshold, default is False.
            :param score_threshold:         Score threshold, default is 0.5.
            :param timeout:                 Total timeout in seconds, default is None. If None, no timeout is set.

        Returns:
            RetrieveChunksResult object.
        """

        import aiohttp
        log = get_logger()

        if not query or not query.strip():
            raise RAGFlowError(message="Query is required", code=400)
        if not dataset_id or not dataset_id.strip():
            raise RAGFlowError(message="Dataset ID is required", code=400)
        if top_k < 1 or top_k > 500:
            raise RAGFlowError(message="top_k must be between 1 and 500", code=400)
        if score_threshold_enabled and (score_threshold < 0 or score_threshold > 1):
            raise RAGFlowError(message="score_threshold must be between 0 and 1", code=400)

        if vector_chunk_size is None:
            vector_chunk_size = max(2, 1 << ((top_k - 1).bit_length()))

        # Use default base URL and API key if not provided
        if not base_url or not base_url.strip():
            base_url = self.default_base_url
            if not base_url or not base_url.strip():
                raise RAGFlowError(message="Base URL is required", code=400)

        if not api_key or not api_key.strip():
            api_key = self.default_api_key
            if not api_key or not api_key.strip():
                raise RAGFlowError(message="API key is required", code=401)

        log.info("Starting retrieve_chunks...")

        # Build the request URL
        url = f"{base_url}/retrieval"

        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Prepare the request payload
        payload = {
            "question": query,
            "top_k": vector_chunk_size,
            "dataset_ids": [dataset_id],
            "page": 1,
            "page_size": top_k,
            "similarity_threshold": score_threshold if score_threshold_enabled else 1e-6,
            "vector_similarity_weight": weights,
            "keyword": True,
            "highlight": False,
        }

        log.debug(f"Retrieving chunks from RAGFlow API: {url}, data = {json.dumps(payload)}, headers = {headers}, "
                  f"total timeout = {(str(timeout) + "s") if timeout is not None and timeout > 0 else 'no'}.")

        try:
            # Create a timeout object if timeout is specified
            timeout_obj = aiohttp.ClientTimeout(total=timeout) if timeout is not None and timeout > 0 else None

            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()

                        code = data.get("code", None)
                        if code is None or not isinstance(code, int) or code != 0:
                            log.error(f"RAGFlow API error: {data}.")
                            raise RAGFlowError(message=f"RAGFlow API error",
                                               code=_ragflow_code_dict.get(code, 500))

                        result = RetrieveChunksResult.model_validate(data)

                        log.debug(f"Retrieved chunks:\n"
                                  f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
                        return result
                    if response.status == 404:
                        error_text = await response.text()
                        log.error(f"Dataset or RAGFlow API endpoint not found: url = {url}, "
                                  f"status = {response.status}, response = {error_text}.")
                        raise RAGFlowError(message=f"Dataset or RAGFlow API endpoint not found", code=response.status)
                    else:
                        error_text = await response.text()
                        raise RAGFlowError(message=f"Failed to retrieve chunks: {response.status} - {error_text}",
                                           code=response.status)

        except asyncio.TimeoutError:
            log.error(f"Timeout while retrieving chunks from RAGFlow API, total timeout is {timeout}s.")
            raise RAGFlowError(message=f"Timeout while retrieving chunks from RAGFlow API, total timeout is {timeout}s",
                               code=408)
        except RAGFlowError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while retrieving chunks from RAGFlow API: {str(e)}.\n{traceback.format_exc()}")
            raise RAGFlowError(message=f"Error while retrieving chunks from RAGFlow API: {str(e)}", code=500)

    async def list_knowledge_bases(self,
                                   name_filter: str | None = None,
                                   base_url: str = None,
                                   api_key: str = None,
                                   page: int | None = 1,
                                   limit: int | None = 20,
                                   timeout: int | None = None,
                                   ) -> ListKnowledgeBasesResult:
        """Lists knowledge bases.

        Args:
            :param name_filter:             Filter by name, default is None.
            :param base_url:                Base URL, default is None to use the default base URL
            :param api_key:                 API key, default is None to use the default API key
            :param page:                    Page number, default is 1.
            :param limit:                   Number of items returned, default is 20.
            :param timeout:                 Total timeout in seconds, default is None. If None, no timeout is set.

        Returns:
            ListKnowledgeBasesResult object.

        - API: GET /api/v1/datasets?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}&name={dataset_name}&id={dataset_id}
        """

        import aiohttp
        log = get_logger()

        # Use default base URL and API key if not provided
        if not base_url or not base_url.strip():
            base_url = self.default_base_url
            if not base_url or not base_url.strip():
                raise RAGFlowError(message="Base URL is required", code=400)

        if not api_key or not api_key.strip():
            api_key = self.default_api_key
            if not api_key or not api_key.strip():
                raise RAGFlowError(message="API key is required", code=401)

        log.info("Starting list_knowledge_bases...")

        # Build the request URL
        url = f"{base_url}/datasets"

        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Prepare the query parameters
        params = {}
        if page is not None and page > 0:
            params["page"] = str(page)
        if limit is not None and limit > 0:
            params["page_size"] = str(limit)
        if name_filter and name_filter.strip():
            params["name"] = name_filter.strip()
        params["orderby"] = "update_time"
        params["desc"] = "true"

        log.debug(f"Listing knowledge bases from RAGFlow API: {url}, params = {params}, headers = {headers}, "
                  f"total timeout = {(str(timeout) + 's') if timeout is not None and timeout > 0 else 'no'}.")

        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout) if timeout is not None and timeout > 0 else None

            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        code = data.get("code", None)
                        if code is None or not isinstance(code, int) or code != 0:
                            log.error(f"RAGFlow API error: {data}.")
                            raise RAGFlowError(message=f"RAGFlow API error",
                                               code=_ragflow_code_dict.get(code, 500))

                        result = ListKnowledgeBasesResult.model_validate(data)

                        log.debug(f"Got knowledge bases:\n"
                                  f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
                        return result
                    if response.status == 404:
                        error_text = await response.text()
                        log.error(f"RAGFlow API endpoint not found: url = {url}, status = {response.status}, "
                                  f"response = {error_text}.")
                        raise RAGFlowError(message=f"RAGFlow API endpoint not found", code=response.status)
                    else:
                        error_text = await response.text()
                        raise RAGFlowError(message=f"Failed to list knowledge bases: {response.status} - {error_text}",
                                           code=response.status)
        except asyncio.TimeoutError:
            log.error(f"Timeout while listing knowledge bases from RAGFlow API, total timeout is {timeout}s.")
            raise RAGFlowError(
                message=f"Timeout while listing knowledge bases from RAGFlow API, total timeout is {timeout}s",
                code=408)
        except RAGFlowError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while listing knowledge bases from RAGFlow API: {str(e)}.\n{traceback.format_exc()}")
            raise RAGFlowError(message=f"Error while listing knowledge bases from RAGFlow API: {str(e)}", code=500)

    async def get_knowledge_base(self,
                                 dataset_id: str,
                                 base_url: str = None,
                                 api_key: str = None,
                                 timeout: int | None = None,
                                 ) -> GetKnowledgeBaseResult:
        """Gets knowledge base details(metadata and description) of  by knowledge base ID (dataset_id).

        Args:
            :param dataset_id: Knowledge ID.
            :param base_url:                Base URL, default is None to use the default base URL
            :param api_key:                 API key, default is None to use the default API key
            :param timeout:                 Total timeout in seconds, default is None. If None, no timeout is set.

        Returns:
            GetKnowledgeBaseResult object.

        - API: GET /api/v1/datasets?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}&name={dataset_name}&id={dataset_id}
        """

        import aiohttp
        log = get_logger()

        if not dataset_id or not dataset_id.strip():
            raise RAGFlowError(message="Dataset ID is required", code=400)

        # Use default base URL and API key if not provided
        if not base_url or not base_url.strip():
            base_url = self.default_base_url
            if not base_url or not base_url.strip():
                raise RAGFlowError(message="Base URL is required", code=400)

        if not api_key or not api_key.strip():
            api_key = self.default_api_key
            if not api_key or not api_key.strip():
                raise RAGFlowError(message="API key is required", code=401)

        log.info("Starting get_knowledge_base...")

        # Build the request URL
        url = f"{base_url}/datasets"

        # Prepare the query parameters
        params = {
            "id": dataset_id,
        }

        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        log.debug(f"Getting knowledge base info from RAGFlow API: {url}, params = {params}, headers = {headers}, "
                  f"total timeout = {(str(timeout) + 's') if timeout is not None and timeout > 0 else 'no'}.")

        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout) if timeout is not None and timeout > 0 else None

            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        code = data.get("code", None)
                        if code is None or not isinstance(code, int) or code != 0:
                            log.error(f"RAGFlow API error: {data}.")
                            raise RAGFlowError(message=f"RAGFlow API error",
                                               code=_ragflow_code_dict.get(code, 500))

                        result_list = ListKnowledgeBasesResult.model_validate(data)
                        if not result_list.data or len(result_list.data) < 1:
                            raise RAGFlowError(message=f"Knowledge base with ID '{dataset_id}' not found", code=404)

                        result = result_list.data[0]

                        log.debug(f"Got knowledge base info:\n"
                                  f"{result.model_dump_json(indent=2, exclude_none=True, exclude_unset=True)}.")
                        return result
                    if response.status == 404:
                        error_text = await response.text()
                        log.error(f"Knowledge base ID '{dataset_id}' or RAGFlow API endpoint not found: url = {url}, "
                                  f"status = {response.status}, response = {error_text}.")
                        raise RAGFlowError(
                            message=f"Knowledge base ID '{dataset_id}' or RAGFlow API endpoint not found",
                            code=response.status)
                    else:
                        error_text = await response.text()
                        raise RAGFlowError(
                            message=f"Failed to get knowledge base with ID '{dataset_id}': {response.status} - {error_text}",
                            code=response.status)

        except asyncio.TimeoutError:
            log.error(
                f"Timeout while getting knowledge base with ID '{dataset_id}' from RAGFlow API, total timeout is {timeout}s.")
            raise RAGFlowError(
                message=f"Timeout while getting knowledge base with ID '{dataset_id}' from RAGFlow API, total timeout is {timeout}s",
                code=408)
        except RAGFlowError as e:
            raise e
        except Exception as e:
            import traceback
            log.error(f"Error while getting knowledge base with ID '{dataset_id}' from RAGFlow API: {str(e)}.\n"
                      f"{traceback.format_exc()}")
            raise RAGFlowError(
                message=f"Error while getting knowledge base with ID '{dataset_id}' from RAGFlow API: {str(e)}",
                code=500)


def get_api(name: str = 'default', default_base_url: str = None, default_api_key: str = None) -> 'RAGFlowKnowledgeAPI':
    """See RAGFlowKnowledgeAPI.get_api(...) for details."""

    return RAGFlowKnowledgeAPI.get_api(name, default_base_url, default_api_key)
