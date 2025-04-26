import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ragflow_knowledge_mcp_server.schema.search_knowledge_types import SearchKnowledgeResult, Knowledge


class TestSearchKnowledgeResult(unittest.TestCase):
    def test_get_simple_text(self):
        # Test case 1: No knowledge found
        result = SearchKnowledgeResult(knowledge_list=[], knowledge_base_id=None)
        print(result.get_simple_text())
        self.assertEqual(result.get_simple_text(), "**No knowledge found.**")

        # Test case 2: Knowledge found without document name
        knowledge = Knowledge(score=0.9, content="Sample content")
        result = SearchKnowledgeResult(knowledge_list=[knowledge], knowledge_base_id="12345")
        print(result.get_simple_text())
        expected_output = (
            "**Found 1 knowledge(s)** (base ID: 12345):\n\n"
            "1. Sample content (score: 0.9)"
        )
        self.assertEqual(result.get_simple_text(), expected_output)

        # Test case 3: Knowledge found with document name
        knowledge = Knowledge(score=0.8, content="Another sample content")
        result = SearchKnowledgeResult(knowledge_list=[knowledge], knowledge_base_id="67890")
        print(result.get_simple_text())
        expected_output = (
            "**Found 1 knowledge(s)** (base ID: 67890):\n\n"
            "1. Another sample content (score: 0.8)"
        )
        self.assertEqual(result.get_simple_text(), expected_output)

        # Test case 4: Multiple knowledge entries
        knowledge1 = Knowledge(score=0.7, content="Content 1")
        knowledge2 = Knowledge(score=0.6, content="Content 2")
        result = SearchKnowledgeResult(knowledge_list=[knowledge1, knowledge2], knowledge_base_id="54321")
        print(result.get_simple_text())
        expected_output = (
            "**Found 2 knowledge(s)** (base ID: 54321):\n\n"
            "1. Content 1 (score: 0.7)\n"
            "2. Content 2 (score: 0.6)"
        )
        self.assertEqual(result.get_simple_text(), expected_output)
