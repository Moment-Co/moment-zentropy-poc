#!/usr/bin/env python3
"""
Advanced ZeroEntropy Example
Demonstrates advanced features: metadata filtering, reranking, snippets, and pages
"""

import os
import time
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

# Load environment variables
load_dotenv()

def main():
    """Main function demonstrating advanced ZeroEntropy features"""
    
    # Check if API key is set
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("❌ Error: ZEROENTROPY_API_KEY not found in environment variables")
        print("Please set your API key in the .env file")
        return
    
    try:
        # Initialize ZeroEntropy client
        print("🚀 Initializing ZeroEntropy client...")
        zclient = ZeroEntropy()
        print("✅ Client initialized successfully")
        
        # Create a collection for advanced demo
        collection_name = "advanced_demo"
        print(f"\n📁 Creating collection: {collection_name}")
        try:
            zclient.collections.add(collection_name=collection_name)
            print("✅ Collection created successfully")
        except ConflictError:
            print("ℹ️  Collection already exists, continuing...")
        
        # Add multiple documents with different metadata
        documents_data = [
            {
                "path": "docs/ai_overview.txt",
                "content": {
                    "type": "text",
                    "text": "Artificial Intelligence (AI) is transforming industries across the globe. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions. Deep learning has revolutionized computer vision and natural language processing."
                },
                "metadata": {
                    "category": "technology",
                    "topic": "AI",
                    "difficulty": "intermediate",
                    "tags": ["machine learning", "deep learning", "computer vision"]
                }
            },
            {
                "path": "docs/business_strategy.txt",
                "content": {
                    "type": "text",
                    "text": "Business strategy involves making long-term decisions about how to allocate resources and compete in the marketplace. Successful strategies often focus on creating unique value propositions and building sustainable competitive advantages."
                },
                "metadata": {
                    "category": "business",
                    "topic": "strategy",
                    "difficulty": "beginner",
                    "tags": ["strategy", "competitive advantage", "value proposition"]
                }
            },
            {
                "path": "docs/data_science.txt",
                "content": {
                    "type": "text",
                    "text": "Data science combines statistics, programming, and domain expertise to extract insights from data. It involves data collection, cleaning, analysis, and visualization to support decision-making processes."
                },
                "metadata": {
                    "category": "technology",
                    "topic": "data science",
                    "difficulty": "advanced",
                    "tags": ["statistics", "programming", "data analysis", "visualization"]
                }
            }
        ]
        
        print(f"\n📄 Adding {len(documents_data)} documents to collection...")
        for doc_data in documents_data:
            try:
                zclient.documents.add(
                    collection_name=collection_name,
                    path=doc_data["path"],
                    content=doc_data["content"],
                    metadata=doc_data["metadata"]
                )
                print(f"✅ Added: {doc_data['path']}")
            except ConflictError:
                print(f"ℹ️  Document already exists: {doc_data['path']}")
        
        # Wait for all documents to be indexed
        print("\n⏳ Waiting for documents to be indexed...")
        all_indexed = False
        while not all_indexed:
            all_indexed = True
            for doc_data in documents_data:
                status = zclient.documents.get_info(
                    collection_name=collection_name,
                    path=doc_data["path"]
                )
                if status.document.index_status != "indexed":
                    all_indexed = False
                    print(f"⏳ {doc_data['path']}: {status.document.index_status}")
                    break
            if not all_indexed:
                time.sleep(2)
        
        print("✅ All documents are indexed and ready for queries")
        
        # Demonstrate metadata filtering
        print(f"\n🔍 Querying with metadata filter (technology category only):")
        response = zclient.queries.top_documents(
            collection_name=collection_name,
            query="learning and analysis",
            k=5,
            filter={"category": {"$eq": "technology"}},
            include_metadata=True
        )
        
        print(f"✅ Found {len(response.results)} technology documents:")
        for i, result in enumerate(response.results, 1):
            print(f"  {i}. {result.path} (Score: {result.score:.4f})")
            if result.metadata:
                print(f"     Category: {result.metadata.get('category', 'N/A')}")
                print(f"     Topic: {result.metadata.get('topic', 'N/A')}")
        
        # Demonstrate snippet queries
        print(f"\n🔍 Querying for snippets with precise responses:")
        snippets = zclient.queries.top_snippets(
            collection_name=collection_name,
            query="machine learning algorithms",
            k=3,
            precise_responses=True,
            include_document_metadata=True
        )
        
        print(f"✅ Found {len(snippets.results)} relevant snippets:")
        for i, snippet in enumerate(snippets.results, 1):
            print(f"  {i}. Document: {snippet.path}")
            print(f"     Content: {snippet.content[:100]}...")
            print(f"     Score: {snippet.score:.4f}")
        
        # Demonstrate page queries (for multi-page documents)
        print(f"\n🔍 Querying for pages (simulating multi-page content):")
        # Create a multi-page document
        multi_page_content = {
            "type": "text-pages",
            "pages": [
                "Page 1: Introduction to ZeroEntropy and its capabilities for document retrieval.",
                "Page 2: Advanced features including metadata filtering, reranking, and snippet extraction.",
                "Page 3: Best practices for implementing ZeroEntropy in production environments."
            ]
        }
        
        try:
            zclient.documents.add(
                collection_name=collection_name,
                path="docs/multi_page_guide.txt",
                content=multi_page_content,
                metadata={"type": "guide", "pages": 3}
            )
            print("✅ Added multi-page document")
        except ConflictError:
            print("ℹ️  Multi-page document already exists")
        
        # Wait for indexing and query pages
        time.sleep(3)
        pages = zclient.queries.top_pages(
            collection_name=collection_name,
            query="production environments",
            k=2,
            include_content=True
        )
        
        print(f"✅ Found {len(pages.results)} relevant pages:")
        for i, page in enumerate(pages.results, 1):
            print(f"  {i}. Document: {page.path}, Page: {page.page_index}")
            print(f"     Content: {page.content[:80]}...")
            print(f"     Score: {page.score:.4f}")
        
        # Demonstrate reranking
        print(f"\n🔍 Demonstrating reranking with custom model:")
        # Get top documents first
        base_results = zclient.queries.top_documents(
            collection_name=collection_name,
            query="data processing",
            k=3,
            include_metadata=True
        )
        
        if base_results.results:
            print("Base search results before reranking:")
            for i, result in enumerate(base_results.results, 1):
                print(f"  {i}. {result.path} (Score: {result.score:.4f})")
            
            # Rerank the results
            try:
                rerank_result = zclient.models.rerank(
                    query="data processing",
                    documents=[result.path for result in base_results.results],
                    model="zerank-1-small",
                    top_n=3
                )
                
                print("\nReranked results:")
                for i, result in enumerate(rerank_result.results, 1):
                    doc_path = base_results.results[result.index].path
                    print(f"  {i}. {doc_path} (New Score: {result.relevance_score:.4f})")
            except Exception as e:
                print(f"ℹ️  Reranking not available: {e}")
        
        # Get final collection status
        print(f"\n📊 Final collection status:")
        status = zclient.status.get(collection_name=collection_name)
        print(f"  Total documents: {status.num_documents}")
        print(f"  Indexed documents: {status.num_indexed_documents}")
        print(f"  Failed documents: {status.num_failed_documents}")
        
        print("\n🎉 Advanced example completed successfully!")
        
    except APIStatusError as e:
        print(f"❌ API Status Error: {e}")
        print("Please check your API key and network connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error details above")

if __name__ == "__main__":
    main()
