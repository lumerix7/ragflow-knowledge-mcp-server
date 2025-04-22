from .server import serve


def main():
    """RAGFlow Knowledge MCP Server Main Entry Point"""

    import os
    import argparse

    if os.getenv("SIMP_LOGGER_LOG_FILE") is None:
        os.environ["SIMP_LOGGER_LOG_FILE"] = os.path.join(
            os.path.expanduser("~"), "logs", "ragflow-knowledge-mcp-server", "mcp.log")
    if os.getenv("SIMP_LOGGER_LOG_CONSOLE_ENABLED") is None:
        os.environ["SIMP_LOGGER_LOG_CONSOLE_ENABLED"] = "False"

    parser = argparse.ArgumentParser(
        description="RAGFlow Knowledge MCP Server: A server for RAGFlow Knowledge Base"
    )
    parser.add_argument("--config", type=str, help="Path to the config file")

    args = parser.parse_args()
    serve(args.config)


if __name__ == "__main__":
    main()
