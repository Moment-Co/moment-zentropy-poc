#!/usr/bin/env python3
"""
Quick Start Script for ZeroEntropy
A minimal example to get you started quickly
"""

import os
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

def quick_start():
    """Quick start function with minimal setup"""
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("ZEROENTROPY_API_KEY")
    if not api_key:
        print("❌ ZEROENTROPY_API_KEY not found!")
        print("Please create a .env file with your API key:")
        print("1. Copy env.example to .env")
        print("2. Add your ZeroEntropy API key to .env")
        print("3. Run this script again")
        return
    
    print("🚀 ZeroEntropy Quick Start")
    print("=" * 40)
    
    try:
        # Initialize client
        client = ZeroEntropy()
        print("✅ Client initialized")
        
        # Create collection
        collection_name = "quickstart"
        try:
            client.collections.add(collection_name=collection_name)
            print("✅ Collection created")
        except ConflictError:
            print("ℹ️  Collection already exists")
        
        # Add a simple document
        client.documents.add(
            collection_name=collection_name,
            path="hello.txt",
            content={"type": "text", "text": "Hello from ZeroEntropy! This is a quick start example."},
            metadata={"demo": "true"}
        )
        print("✅ Document added")
        
        # Simple query
        results = client.queries.top_documents(
            collection_name=collection_name,
            query="Hello",
            k=1
        )
        
        print(f"✅ Query successful: {len(results.results)} result(s)")
        print(f"   Found: {results.results[0].path}")
        
        print("\n🎉 Quick start completed successfully!")
        print("\nNext steps:")
        print("- Run: python basic_example.py")
        print("- Run: python advanced_example.py")
        print("- Run: python async_example.py")
        
    except APIStatusError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_start()
