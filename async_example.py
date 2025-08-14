#!/usr/bin/env python3
"""
Async ZeroEntropy Example
Demonstrates async/await pattern for better performance and concurrent operations
"""

import asyncio
import os
import time
from dotenv import load_dotenv
from zeroentropy import AsyncZeroEntropy, ConflictError, APIStatusError

# Load environment variables
load_dotenv()

async def main():
    """Main async function demonstrating ZeroEntropy async usage"""
    
    # Check if API key is set
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("❌ Error: ZEROENTROPY_API_KEY not found in environment variables")
        print("Please set your API key in the .env file")
        return
    
    try:
        # Initialize AsyncZeroEntropy client
        print("🚀 Initializing AsyncZeroEntropy client...")
        zclient = AsyncZeroEntropy()
        print("✅ Async client initialized successfully")
        
        # Create a collection for async demo
        collection_name = "async_demo"
        print(f"\n📁 Creating collection: {collection_name}")
        try:
            await zclient.collections.add(collection_name=collection_name)
            print("✅ Collection created successfully")
        except ConflictError:
            print("ℹ️  Collection already exists, continuing...")
        
        # Add multiple documents concurrently
        documents_data = [
            {
                "path": "docs/async_doc1.txt",
                "content": {
                    "type": "text",
                    "text": "Asynchronous programming allows multiple operations to run concurrently, improving performance and responsiveness. This is especially useful for I/O-bound operations like API calls and database queries."
                },
                "metadata": {
                    "category": "programming",
                    "topic": "async",
                    "difficulty": "intermediate"
                }
            },
            {
                "path": "docs/async_doc2.txt",
                "content": {
                    "type": "text",
                    "text": "Python's asyncio library provides a framework for writing concurrent code using coroutines, event loops, and tasks. It's particularly effective for handling many concurrent network connections."
                },
                "metadata": {
                    "category": "programming",
                    "topic": "asyncio",
                    "difficulty": "advanced"
                }
            },
            {
                "path": "docs/async_doc3.txt",
                "content": {
                    "type": "text",
                    "text": "Concurrent programming with async/await patterns can significantly improve application performance by allowing non-blocking operations and better resource utilization."
                },
                "metadata": {
                    "category": "programming",
                    "topic": "concurrency",
                    "difficulty": "intermediate"
                }
            }
        ]
        
        print(f"\n📄 Adding {len(documents_data)} documents concurrently...")
        
        # Add documents concurrently using asyncio.gather
        add_tasks = []
        for doc_data in documents_data:
            task = zclient.documents.add(
                collection_name=collection_name,
                path=doc_data["path"],
                content=doc_data["content"],
                metadata=doc_data["metadata"]
            )
            add_tasks.append(task)
        
        # Execute all add operations concurrently
        try:
            await asyncio.gather(*add_tasks)
            print("✅ All documents added successfully")
        except Exception as e:
            print(f"⚠️  Some documents may not have been added: {e}")
        
        # Wait for all documents to be indexed concurrently
        print("\n⏳ Waiting for documents to be indexed concurrently...")
        
        async def wait_for_indexing(doc_path):
            """Wait for a single document to be indexed"""
            while True:
                status = await zclient.documents.get_info(
                    collection_name=collection_name,
                    path=doc_path
                )
                if status.document.index_status == "indexed":
                    return f"✅ {doc_path}: indexed"
                elif status.document.index_status in ["parsing_failed", "not_parsed"]:
                    return f"❌ {doc_path}: {status.document.index_status}"
                await asyncio.sleep(1)
        
        # Monitor indexing status concurrently
        indexing_tasks = [
            wait_for_indexing(doc_data["path"]) 
            for doc_data in documents_data
        ]
        
        # Wait for all documents to be indexed
        indexing_results = await asyncio.gather(*indexing_tasks)
        for result in indexing_results:
            print(result)
        
        print("✅ All documents are indexed and ready for queries")
        
        # Perform multiple queries concurrently
        print(f"\n🔍 Performing multiple queries concurrently...")
        
        queries = [
            ("async programming", "async"),
            ("concurrent operations", "concurrency"),
            ("python asyncio", "asyncio")
        ]
        
        async def execute_query(query_text, topic):
            """Execute a single query"""
            try:
                response = await zclient.queries.top_documents(
                    collection_name=collection_name,
                    query=query_text,
                    k=2,
                    include_metadata=True
                )
                return f"Query '{query_text}': {len(response.results)} results"
            except Exception as e:
                return f"Query '{query_text}' failed: {e}"
        
        # Execute all queries concurrently
        query_tasks = [
            execute_query(query_text, topic) 
            for query_text, topic in queries
        ]
        
        query_results = await asyncio.gather(*query_tasks)
        for result in query_results:
            print(f"  {result}")
        
        # Demonstrate concurrent document operations
        print(f"\n📄 Performing concurrent document operations...")
        
        async def get_document_info(doc_path):
            """Get information for a single document"""
            try:
                info = await zclient.documents.get_info(
                    collection_name=collection_name,
                    path=doc_path,
                    include_content=False
                )
                return f"📄 {doc_path}: {info.document.index_status}"
            except Exception as e:
                return f"❌ {doc_path}: {e}"
        
        # Get info for all documents concurrently
        info_tasks = [
            get_document_info(doc_data["path"]) 
            for doc_data in documents_data
        ]
        
        info_results = await asyncio.gather(*info_tasks)
        for result in info_results:
            print(f"  {result}")
        
        # Demonstrate concurrent snippet queries
        print(f"\n🔍 Performing concurrent snippet queries...")
        
        snippet_queries = [
            "async programming",
            "concurrent operations",
            "python asyncio"
        ]
        
        async def get_snippets(query_text):
            """Get snippets for a single query"""
            try:
                snippets = await zclient.queries.top_snippets(
                    collection_name=collection_name,
                    query=query_text,
                    k=2,
                    precise_responses=True
                )
                return f"Snippets for '{query_text}': {len(snippets.results)} found"
            except Exception as e:
                return f"Snippets for '{query_text}' failed: {e}"
        
        # Execute snippet queries concurrently
        snippet_tasks = [get_snippets(query) for query in snippet_queries]
        snippet_results = await asyncio.gather(*snippet_tasks)
        
        for result in snippet_results:
            print(f"  {result}")
        
        # Get final collection status
        print(f"\n📊 Final collection status:")
        status = await zclient.status.get(collection_name=collection_name)
        print(f"  Total documents: {status.num_documents}")
        print(f"  Indexed documents: {status.num_indexed_documents}")
        print(f"  Failed documents: {status.num_failed_documents}")
        
        print("\n🎉 Async example completed successfully!")
        
    except APIStatusError as e:
        print(f"❌ API Status Error: {e}")
        print("Please check your API key and network connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error details above")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
