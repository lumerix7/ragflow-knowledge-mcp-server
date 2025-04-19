import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from ragflow_knowledge_mcp_server.ragflow import RAGFlowKnowledgeAPI, get_api
from ragflow_knowledge_mcp_server.logger import get_logger
from ragflow_knowledge_mcp_server.service import list_knowledge_bases
from ragflow_knowledge_mcp_server.properties import MCPServerProperties


class TestListKnowledgeBases(unittest.TestCase):
    def test_list_knowledge_bases(self):
        log = get_logger()
        log.setLevel("DEBUG")

        api = RAGFlowKnowledgeAPI("http://127.0.0.1:9388/api/v1", "ragflow-M2YTVlMmIyMWI2ODExZjA5OTJiNWUwNm")

        # Call the function and check the result
        result = asyncio.run(api.list_knowledge_bases(), debug=True)

        log.error(f"Result: {type(result)}")
        result_json = result.model_dump_json(indent=2)

        log.info(f"Result: {result_json}")

    def test_list_knowledge_bases_mcp(self):
        log = get_logger()
        log.setLevel("DEBUG")

        if False:
            api = get_api()
            properties = MCPServerProperties()
            properties.load("D:\\data\\ragflow-knowledge-mcp-server\\config-stdio.yaml")

            # Call the function and check the result
            result = asyncio.run(list_knowledge_bases(properties=properties,
                                                      api=api,
                                                      args={
                                                      }),
                                 )
            print(result)
