#!/usr/bin/env python3
"""
Basic ZeroEntropy Example
Demonstrates core functionality: collections, documents, and queries
"""

import os
import time
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

# Load environment variables
load_dotenv()

def main():
    """Main function demonstrating basic ZeroEntropy usage"""
    
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
        
        # Create a collection
        collection_name = "demo_collection"
        print(f"\n📁 Creating collection: {collection_name}")
        try:
            zclient.collections.add(collection_name=collection_name)
            print("✅ Collection created successfully")
        except ConflictError:
            print("ℹ️  Collection already exists, continuing...")
        
        # Add a text document
        print(f"\n📄 Adding text document to collection...")
        document = zclient.documents.add(
            collection_name=collection_name,
            path="docs/sample.txt",
            content={
                "type": "text",
                "text": "ZeroEntropy is a powerful document retrieval API that provides low-latency, high-accuracy search over your private corpus. It supports various document types including PDFs, text files, and more.",
            },
            metadata={
                "source": "demo",
                "type": "text",
                "category": "introduction"
            }
        )
        print("✅ Document added successfully")
        
        # Wait for indexing to complete
        print("\n⏳ Waiting for document to be indexed...")
        while True:
            status = zclient.documents.get_info(
                collection_name=collection_name, 
                path="docs/sample.txt"
            )
            if status.document.index_status == "indexed":
                print("✅ Document is indexed and ready for queries")
                break
            elif status.document.index_status in ["parsing_failed", "not_parsed"]:
                print(f"❌ Document indexing failed: {status.document.index_status}")
                return
            print(f"⏳ Current status: {status.document.index_status}")
            time.sleep(1)
        
        # Query the collection
        print(f"\n🔍 Querying collection for: 'powerful API'")
        response = zclient.queries.top_documents(
            collection_name=collection_name,
            query="powerful API",
            k=3,
            include_metadata=True
        )
        
        print(f"✅ Found {len(response.results)} results:")
        for i, result in enumerate(response.results, 1):
            print(f"  {i}. {result.path} (Score: {result.score:.4f})")
            if result.metadata:
                print(f"     Metadata: {result.metadata}")
        
        # Get collection status
        print(f"\n📊 Collection status:")
        status = zclient.status.get(collection_name=collection_name)
        print(f"  Total documents: {status.num_documents}")
        print(f"  Indexed documents: {status.num_indexed_documents}")
        print(f"  Failed documents: {status.num_failed_documents}")
        
        print("\n🎉 Basic example completed successfully!")
        
    except APIStatusError as e:
        print(f"❌ API Status Error: {e}")
        print("Please check your API key and network connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error details above")

if __name__ == "__main__":
    main()
