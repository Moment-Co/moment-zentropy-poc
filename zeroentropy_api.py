"""
ZeroEntropy API Client
Comprehensive wrapper for all ZeroEntropy API endpoints
"""

import requests
import os
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class ZeroEntropyAPI:
    """Client for ZeroEntropy API operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client"""
        self.api_key = api_key or os.getenv('ZEROENTROPY_API_KEY')
        if not self.api_key:
            raise ValueError("ZEROENTROPY_API_KEY not found in environment variables")
        
        self.base_url = "https://api.zeroentropy.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(response, 'status_code', None)}
        except Exception as e:
            return {"error": str(e), "status_code": None}
    
    # Collection Management
    def get_collection_status(self, collection_name: str) -> Dict[str, Any]:
        """Get status of a collection"""
        payload = {"collection_name": collection_name}
        return self._make_request("status/get-status", payload)
    
    def add_collection(self, collection_name: str) -> Dict[str, Any]:
        """Create a new collection"""
        payload = {"collection_name": collection_name}
        return self._make_request("collections/add-collection", payload)
    
    def get_collection_list(self) -> Dict[str, Any]:
        """Get list of all collections"""
        payload = {}
        return self._make_request("collections/get-collection-list", payload)
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection"""
        payload = {"collection_name": collection_name}
        return self._make_request("collections/delete-collection", payload)
    
    # Document Management
    def add_document(self, collection_name: str, path: str, content: Dict[str, Any], 
                    metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a document to a collection according to ZeroEntropy API spec"""
        payload = {
            "collection_name": collection_name,
            "path": path,
            "content": content,
            "metadata": metadata or {}
        }
        
        return self._make_request("documents/add-document", payload)
    
    def update_document(self, collection_name: str, path: str, 
                       metadata: Optional[Dict] = None, 
                       index_status: str = "not_parsed") -> Dict[str, Any]:
        """Update document metadata"""
        payload = {
            "collection_name": collection_name,
            "path": path,
            "metadata": metadata or {},
            "index_status": index_status
        }
        return self._make_request("documents/update-document", payload)
    
    def get_document_info(self, collection_name: str, path: str, 
                         include_content: bool = False) -> Dict[str, Any]:
        """Get information about a specific document"""
        payload = {
            "collection_name": collection_name,
            "path": path,
            "include_content": include_content
        }
        return self._make_request("documents/get-document-info", payload)
    
    def get_document_list(self, collection_name: str, limit: int = 1024, 
                         path_prefix: Optional[str] = None, 
                         path_gt: Optional[str] = None) -> Dict[str, Any]:
        """Get list of documents in a collection"""
        payload = {
            "collection_name": collection_name,
            "limit": limit
        }
        if path_prefix:
            payload["path_prefix"] = path_prefix
        if path_gt:
            payload["path_gt"] = path_gt
        return self._make_request("documents/get-document-info-list", payload)
    
    def delete_document(self, collection_name: str, path: str) -> Dict[str, Any]:
        """Delete a document from a collection"""
        payload = {
            "collection_name": collection_name,
            "path": path
        }
        return self._make_request("documents/delete-document", payload)
    
    def get_page_info(self, collection_name: str, path: str, page_index: int, 
                     include_content: bool = False) -> Dict[str, Any]:
        """Get information about a specific page in a document"""
        payload = {
            "collection_name": collection_name,
            "path": path,
            "page_index": page_index,
            "include_content": include_content
        }
        return self._make_request("documents/get-page-info", payload)
    
    # Query Operations
    def search_documents(self, collection_name: str, query: str, k: int = 10, 
                        filter_dict: Optional[Dict] = None, 
                        include_metadata: bool = True, 
                        reranker: Optional[str] = None, 
                        latency_mode: str = "low") -> Dict[str, Any]:
        """Search for top documents"""
        payload = {
            "collection_name": collection_name,
            "query": query,
            "k": k
        }
        
        # Only add optional parameters if they have values
        if filter_dict:
            payload["filter"] = filter_dict
        if include_metadata:
            payload["include_metadata"] = include_metadata
        if reranker:
            payload["reranker"] = reranker
        if latency_mode:
            payload["latency_mode"] = latency_mode
            
        return self._make_request("queries/top-documents", payload)
    
    def search_pages(self, collection_name: str, query: str, k: int = 10, 
                    filter_dict: Optional[Dict] = None, 
                    include_content: bool = False, 
                    latency_mode: str = "low") -> Dict[str, Any]:
        """Search for top pages"""
        payload = {
            "collection_name": collection_name,
            "query": query,
            "k": k
        }
        
        # Only add optional parameters if they have values
        if filter_dict:
            payload["filter"] = filter_dict
        if include_content:
            payload["include_content"] = include_content
        if latency_mode:
            payload["latency_mode"] = latency_mode
            
        return self._make_request("queries/top-pages", payload)
    
    def search_snippets(self, collection_name: str, query: str, k: int = 10, 
                       reranker: Optional[str] = None, 
                       filter_dict: Optional[Dict] = None, 
                       precise_responses: bool = False, 
                       include_document_metadata: bool = False) -> Dict[str, Any]:
        """Search for top snippets"""
        payload = {
            "collection_name": collection_name,
            "query": query,
            "k": k
        }
        
        # Only add optional parameters if they have values
        if reranker:
            payload["reranker"] = reranker
        if filter_dict:
            payload["filter"] = filter_dict
        if precise_responses:
            payload["precise_responses"] = precise_responses
        if include_document_metadata:
            payload["include_document_metadata"] = include_document_metadata
            
        return self._make_request("queries/top-snippets", payload)
    
    # Reranking
    def rerank_documents(self, model: str, query: str, documents: List[str], 
                        top_n: int = 10) -> Dict[str, Any]:
        """Rerank documents using a specific model"""
        payload = {
            "model": model,
            "query": query,
            "top_n": top_n,
            "documents": documents
        }
        return self._make_request("models/rerank", payload)
    
    # Convenience Methods
    def upload_csv_content(self, collection_name: str, file_path: str, 
                          content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload CSV content with sports-specific metadata"""
        try:
            # Create sports-specific metadata if none provided
            if not metadata:
                metadata = {
                    "source": "streamlit_upload",
                    "filename": file_path,
                    "type": "sports_data",
                    "uploaded_at": datetime.now().isoformat()
                }
            
            # First, try to delete any existing document with the same path
            try:
                delete_result = self.delete_document(collection_name, file_path)
                if "error" not in delete_result:
                    print(f"🗑️ Deleted existing document: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not delete existing document: {e}")
            
            # Now upload the new document
            return self.add_csv_document(
                collection_name=collection_name,
                path=file_path,
                csv_content=content,
                metadata=metadata
            )
        except Exception as e:
            return {"error": f"Upload failed: {str(e)}"}
    
    def add_csv_document(self, collection_name: str, path: str, csv_content: str, 
                        metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a CSV document to a collection"""
        content = {
            "type": "text",
            "text": csv_content
        }
        return self.add_document(collection_name, path, content, metadata)
    
    def add_text_document(self, collection_name: str, path: str, text_content: str, 
                         metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a text document to a collection"""
        content = {
            "type": "text",
            "text": text_content
        }
        return self.add_document(collection_name, path, content, metadata)
    
    def search_sports_games(self, collection_name: str, query: str, 
                           venue: Optional[str] = None, 
                           team: Optional[str] = None, 
                           date: Optional[str] = None, 
                           k: int = 10) -> Dict[str, Any]:
        """Search for sports games with metadata filtering"""
        filter_dict = {}
        
        if venue:
            filter_dict["venue"] = {"$eq": venue}
        if team:
            filter_dict["team"] = {"$eq": team}
        if date:
            filter_dict["date"] = {"$eq": date}
        
        return self.search_documents(
            collection_name=collection_name,
            query=query,
            k=k,
            filter_dict=filter_dict,
            include_metadata=True
        )

# Example usage and testing
if __name__ == "__main__":
    # Test the API client
    try:
        api = ZeroEntropyAPI()
        
        # Test collection operations
        collections = api.get_collection_list()
        print("Collections:", collections)
        
        # Test document search
        if collections.get("collections"):
            collection_name = collections["collections"][0]["name"]
            results = api.search_documents(collection_name, "test query", k=5)
            print("Search results:", results)
            
    except Exception as e:
        print(f"Error: {e}")
