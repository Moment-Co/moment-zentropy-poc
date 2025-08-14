#!/usr/bin/env python3
"""
Demo script for Streamlit app functionality
Tests the core ZeroEntropy operations that the Streamlit app will use
"""

import os
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

def demo_streamlit_functionality():
    """Demo the functionality that will be available in the Streamlit app"""
    
    print("🚀 ZeroEntropy Streamlit App Demo")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("ZEROENTROPY_API_KEY")
    
    if not api_key:
        print("❌ ZEROENTROPY_API_KEY not found in .env file")
        print("Please set your API key first")
        return
    
    try:
        # Initialize client
        print("📡 Initializing ZeroEntropy client...")
        client = ZeroEntropy()
        print("✅ Client initialized successfully")
        
        # Test collections operations
        print("\n📁 Testing Collections Operations...")
        
        # Get existing collections
        collections_response = client.collections.get_list()
        collections = collections_response.collection_names
        print(f"   Found {len(collections)} existing collections: {collections}")
        
        # Create a demo collection
        demo_collection = "streamlit_demo"
        try:
            client.collections.add(collection_name=demo_collection)
            print(f"   ✅ Created collection: {demo_collection}")
        except ConflictError:
            print(f"   ℹ️  Collection {demo_collection} already exists")
        
        # Test document operations
        print("\n📄 Testing Document Operations...")
        
        # Add a test document
        test_content = {
            "type": "text",
            "text": "This is a test document for the Streamlit app demo. It contains information about ZeroEntropy and its capabilities for document retrieval and search."
        }
        
        try:
            client.documents.add(
                collection_name=demo_collection,
                path="demo/test_doc.txt",
                content=test_content,
                metadata={"demo": "true", "source": "streamlit_demo"}
            )
            print("   ✅ Added test document successfully")
        except ConflictError:
            print("   ℹ️  Test document already exists")
        
        # Test query operations
        print("\n🔍 Testing Query Operations...")
        
        # Wait a moment for indexing
        import time
        time.sleep(2)
        
        # Query for documents
        results = client.queries.top_documents(
            collection_name=demo_collection,
            query="ZeroEntropy capabilities",
            k=3,
            include_metadata=True
        )
        
        print(f"   ✅ Query successful: {len(results.results)} results")
        for i, result in enumerate(results.results, 1):
            print(f"      {i}. {result.path} (Score: {result.score:.4f})")
        
        # Test status operations
        print("\n📊 Testing Status Operations...")
        
        status = client.status.get_status(collection_name=demo_collection)
        print(f"   Collection Status:")
        print(f"      Total Documents: {status.num_documents}")
        print(f"      Indexed: {status.num_indexed_documents}")
        print(f"      Failed: {status.num_failed_documents}")
        print(f"      Processing: {status.num_parsing_documents + status.num_indexing_documents}")
        
        # Test snippet queries
        print("\n📝 Testing Snippet Queries...")
        
        snippets = client.queries.top_snippets(
            collection_name=demo_collection,
            query="document retrieval",
            k=2,
            precise_responses=True
        )
        
        print(f"   ✅ Snippet query successful: {len(snippets.results)} results")
        for i, snippet in enumerate(snippets.results, 1):
            print(f"      {i}. Content: {snippet.content[:100]}...")
        
        print("\n🎉 All Streamlit app functionality tests passed!")
        print("\nYou can now launch the Streamlit app with:")
        print("   ./launch_streamlit.sh")
        print("   or")
        print("   streamlit run streamlit_app.py")
        
    except APIStatusError as e:
        print(f"❌ API Error: {e}")
        print("Please check your API key and network connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error details above")

if __name__ == "__main__":
    demo_streamlit_functionality()
