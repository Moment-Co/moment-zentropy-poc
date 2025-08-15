#!/usr/bin/env python3
"""
Moment - Sports NLP Search Quickstart
Simple demonstration of the ZeroEntropy API client
"""

import os
from dotenv import load_dotenv
from zeroentropy_api import ZeroEntropyAPI

def main():
    """Quickstart demonstration"""
    print("⚽ Moment - Sports NLP Search Quickstart")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    zeroentropy_key = os.getenv('ZEROENTROPY_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not zeroentropy_key:
        print("❌ ZEROENTROPY_API_KEY not found in .env file")
        print("   Please add your API key to the .env file")
        return
    
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not found - GPT-5 features will be limited")
    
    try:
        # Initialize API client
        print("🔌 Initializing ZeroEntropy API client...")
        api = ZeroEntropyAPI()
        print("✅ API client initialized successfully!")
        
        # Test basic functionality
        print("\n📊 Testing basic functionality...")
        
        # Get collections
        print("   Getting collections...")
        collections = api.get_collection_list()
        if "collections" in collections:
            print(f"   ✅ Found {len(collections['collections'])} collections")
            for col in collections['collections']:
                print(f"      - {col['name']}")
        else:
            print("   ℹ️  No collections found")
        
        # Test collection creation (optional)
        print("\n🔧 Testing collection creation...")
        test_collection = "quickstart_test"
        
        # Check if collection exists
        try:
            status = api.get_collection_status(test_collection)
            print(f"   ℹ️  Collection '{test_collection}' already exists")
        except:
            print(f"   Creating test collection '{test_collection}'...")
            result = api.add_collection(test_collection)
            if "error" not in result:
                print(f"   ✅ Collection '{test_collection}' created successfully!")
            else:
                print(f"   ❌ Failed to create collection: {result.get('error')}")
        
        # Test document upload
        print("\n📄 Testing document upload...")
        test_content = "This is a test document for the quickstart demonstration."
        test_metadata = {
            "type": "test",
            "source": "quickstart",
            "venue": "Test Stadium",
            "team": "Test Team"
        }
        
        result = api.upload_csv_content(
            collection_name=test_collection,
            file_path="quickstart_test.txt",
            content=test_content,
            metadata=test_metadata
        )
        
        if "error" not in result:
            print("   ✅ Test document uploaded successfully!")
            
            # Test search
            print("\n🔍 Testing search functionality...")
            search_results = api.search_documents(
                collection_name=test_collection,
                query="test document",
                k=5
            )
            
            if "error" not in search_results:
                print(f"   ✅ Search successful! Found {len(search_results.get('documents', []))} results")
            else:
                print(f"   ❌ Search failed: {search_results.get('error')}")
        else:
            print(f"   ❌ Document upload failed: {result.get('error')}")
        
        print("\n🎉 Quickstart completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Run the Streamlit app: ./launch.sh")
        print("   2. Upload your sports documents")
        print("   3. Start searching with GPT-5 enhanced mode!")
        
    except Exception as e:
        print(f"❌ Error during quickstart: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file has the correct API keys")
        print("   2. Verify your internet connection")
        print("   3. Check the ZeroEntropy API status")

if __name__ == "__main__":
    main() 
