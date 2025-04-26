import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ragflow_knowledge_mcp_server.logger import get_logger

from ragflow_knowledge_mcp_server.service import search_knowledge
from ragflow_knowledge_mcp_server.properties import MCPServerProperties
from ragflow_knowledge_mcp_server.ragflow import get_api


class TestSearchKnowledge(unittest.TestCase):
    def test_search_knowledge(self):
        log = get_logger()
        log.setLevel("DEBUG")

        if False:
            api = get_api()
            properties = MCPServerProperties()
            properties.load(os.path.join(os.path.expanduser("~"), ".config", "ragflow-knowledge-mcp-server", "config-stdio.yaml"))

            # Call the function and check the result
            result = asyncio.run(search_knowledge(properties=properties,
                                                  api=api,
                                                  dataset=properties.datasets.get(
                                                      "dc9d218a1b2711f0abc75e06b154e83f"),
                                                  args={
                                                      "query": "JVM",
                                                  }),
                                 )
            print(result)
