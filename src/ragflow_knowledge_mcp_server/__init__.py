from .server import serve


def main():
    """RAGFlow Knowledge MCP Server Main Entry Point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="RAGFlow Knowledge MCP Server: A server for RAGFlow Knowledge Base"
    )
    parser.add_argument("--config", type=str, help="Path to the config file")

    args = parser.parse_args()
    serve(args.config)


if __name__ == "__main__":
    main()
