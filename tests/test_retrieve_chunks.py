import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from ragflow_knowledge_mcp_server.ragflow import RAGFlowKnowledgeAPI
from ragflow_knowledge_mcp_server.logger import get_logger


class TestRetrieveChunks(unittest.TestCase):
    def test_retrieve_chunks(self):
        log = get_logger()
        log.setLevel("DEBUG")

        # Test case for the retrieve_chunks function
        api = RAGFlowKnowledgeAPI("http://127.0.0.1:9388/api/v1", "ragflow-M2YTVlMmIyMWI2ODExZjA5OTJiNWUwNm")

        # Example input
        text = "JVM"
        chunk_size = 3

        # Call the function and check the result
        result = asyncio.run(api.retrieve_chunks(
            dataset_id="dc9d218a1b2711f0abc75e06b154e83f",
            query=text,
            top_k=chunk_size,
        ), debug=True)

        log.error(f"Result: {type(result)}")
        result_json = result.model_dump_json(indent=2)

        log.info(f"Result: {result_json}")
