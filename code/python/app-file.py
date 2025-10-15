# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""
This file is the entry point for the NLWeb Sample App.

WARNING: This code is under development and may undergo changes in future releases.
Backwards compatibility is not guaranteed at this time.
"""
import asyncio
import os
from dotenv import load_dotenv

async def main():
    # Load environment variables
    load_dotenv()

    import logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("webserver.middleware.logging_middleware").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    # Initialize router
    import core.router as router
    router.init()

    # Initialize LLM providers
    import core.llm as llm
    llm.init()

    # Initialize retrieval clients
    import core.retriever as retriever
    retriever.init()

    # # === Initialize storage client ===
    # from core.storage import StorageClient  # adjust import path if needed
    # storage_client = await StorageClient.connect(
    #     url=os.environ.get("QDRANT_URL"),
    #     api_key=os.environ.get("QDRANT_API_KEY")
    # )
    # # Attach storage client to the server (so health endpoint can see it)
    # import webserver.aiohttp_server as aio_server
    # aio_server.STORAGE_CLIENT = storage_client  # or server.storage_client depending on your implementation

    print("Starting aiohttp server...")
    from webserver.aiohttp_server import AioHTTPServer
    server = AioHTTPServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
