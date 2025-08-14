#!/usr/bin/env python3
"""
ZeroEntropy Streamlit Application
A comprehensive web interface for managing collections, uploading documents, and querying corpora
"""

import streamlit as st
import os
import time
import base64
import io
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from the current directory
import pathlib
current_dir = pathlib.Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(env_path)

# Import ZeroEntropy
try:
    from zeroentropy import ZeroEntropy, ConflictError, APIStatusError
    ZEROENTROPY_AVAILABLE = True
except ImportError:
    ZEROENTROPY_AVAILABLE = False
    st.error("ZeroEntropy package not available. Please install it first.")

# Import LLM Metadata Filter
try:
    from llm_metadata_filter import LLMMetadataFilter
    LLM_FILTER_AVAILABLE = True
except ImportError:
    LLM_FILTER_AVAILABLE = False
    st.warning("LLM Metadata Filter not available. Basic filtering will be used.")

# Page configuration
st.set_page_config(
    page_title="ZeroEntropy Corpus Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class ZeroEntropyManager:
    """Manager class for ZeroEntropy operations"""
    
    def __init__(self):
        self.client = None
        self.llm_filter = None
        self.initialize_client()
        self.initialize_llm_filter()
    
    def initialize_client(self):
        """Initialize the ZeroEntropy client"""
        try:
            api_key = os.getenv("ZEROENTROPY_API_KEY")
            if not api_key:
                st.error("ZEROENTROPY_API_KEY not found in environment variables")
                st.info(f"Current working directory: {os.getcwd()}")
                st.info(f"Environment file path: {pathlib.Path(__file__).parent / '.env'}")
                st.info(f"Environment file exists: {(pathlib.Path(__file__).parent / '.env').exists()}")
                st.info(f"All environment variables: {dict(os.environ)}")
                return False
            
            self.client = ZeroEntropy()
            st.success("ZeroEntropy client initialized successfully")
            return True
        except Exception as e:
            st.error(f"Failed to initialize ZeroEntropy client: {e}")
            return False
    
    def initialize_llm_filter(self):
        """Initialize the LLM metadata filter"""
        try:
            if LLM_FILTER_AVAILABLE:
                # Pass the existing client to the LLM filter
                self.llm_filter = LLMMetadataFilter(client=self.client)
                return True
            else:
                return False
        except Exception as e:
            st.warning(f"LLM filter not available: {e}")
            return False
    
    def get_collections(self) -> List[str]:
        """Get list of existing collections"""
        try:
            if not self.client:
                st.error("Client not initialized in get_collections")
                return []
            
            st.info(f"Getting collections with client: {self.client}")
            collections_response = self.client.collections.get_list()
            st.info(f"Collections response: {collections_response}")
            st.info(f"Collection names: {collections_response.collection_names}")
            
            return collections_response.collection_names
        except Exception as e:
            st.error(f"Failed to get collections: {e}")
            st.error(f"Exception type: {type(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection"""
        try:
            if not self.client:
                return False
            self.client.collections.add(collection_name=collection_name)
            return True
        except ConflictError:
            st.warning(f"Collection '{collection_name}' already exists")
            return False
        except Exception as e:
            st.error(f"Failed to create collection: {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            if not self.client:
                return False
            self.client.collections.delete(collection_name=collection_name)
            return True
        except Exception as e:
            st.error(f"Failed to delete collection: {e}")
            return False
    
    def upload_document(self, collection_name: str, file_path: str, 
                       content_type: str, metadata: Dict[str, str] = None) -> bool:
        """Upload a document to a collection"""
        try:
            if not self.client:
                return False
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Prepare content based on type
            if content_type == "text":
                content = {
                    "type": "text",
                    "text": file_content.decode('utf-8', errors='ignore')
                }
            elif content_type == "auto":
                # For PDFs and other files, use auto parsing
                base64_data = base64.b64encode(file_content).decode()
                content = {
                    "type": "auto",
                    "base64_data": base64_data
                }
            else:
                st.error(f"Unsupported content type: {content_type}")
                return False
            
            # Upload document
            self.client.documents.add(
                collection_name=collection_name,
                path=file_path,
                content=content,
                metadata=metadata or {}
            )
            return True
            
        except Exception as e:
            st.error(f"Failed to upload document: {e}")
            return False
    
    def get_document_status(self, collection_name: str, file_path: str) -> Optional[str]:
        """Get the status of a document"""
        try:
            if not self.client:
                return None
            status = self.client.documents.get_info(
                collection_name=collection_name,
                path=file_path
            )
            return status.document.index_status
        except Exception as e:
            return None
    
    def query_collection(self, collection_name: str, query: str, 
                        query_type: str = "documents", k: int = 5) -> List[Dict]:
        """Query a collection"""
        try:
            if not self.client:
                st.error("Client not initialized in query_collection")
                return []
            
            st.info(f"Querying collection: '{collection_name}' with query: '{query}'")
            st.info(f"Client status: {self.client is not None}")
            
            if query_type == "documents":
                response = self.client.queries.top_documents(
                    collection_name=collection_name,
                    query=query,
                    k=k,
                    include_metadata=True
                )
                return [
                    {
                        "type": "document",
                        "path": result.path,
                        "score": result.score,
                        "metadata": result.metadata
                    }
                    for result in response.results
                ]
            elif query_type == "pages":
                response = self.client.queries.top_pages(
                    collection_name=collection_name,
                    query=query,
                    k=k,
                    include_content=True
                )
                return [
                    {
                        "type": "page",
                        "path": result.path,
                        "page_index": result.page_index,
                        "score": result.score,
                        "content": result.content
                    }
                    for result in response.results
                ]
            elif query_type == "snippets":
                response = self.client.queries.top_snippets(
                    collection_name=collection_name,
                    query=query,
                    k=k,
                    precise_responses=True,
                    include_document_metadata=True
                )
                return [
                    {
                        "type": "snippet",
                        "path": result.path,
                        "score": result.score,
                        "content": result.content,
                        "start_index": result.start_index,
                        "end_index": result.end_index
                    }
                    for result in response.results
                ]
            else:
                return []
                
        except Exception as e:
            st.error(f"Query failed: {e}")
            return []
    
    def query_collection_llm_enhanced(self, collection_name: str, query: str, k: int = 10) -> Dict[str, Any]:
        """Query collection using LLM-enhanced metadata filtering"""
        try:
            if not self.client:
                return {"error": "ZeroEntropy client not initialized"}
            
            st.info(f"LLM query - Collection: '{collection_name}', Query: '{query}', k: {k}")
            st.info(f"LLM filter available: {self.llm_filter is not None}")
            
            if not self.llm_filter:
                # Fallback to basic query
                return {
                    "query": query,
                    "total_results": 0,
                    "llm_response": "LLM filtering not available. Using basic search.",
                    "zeroentropy_results": [],
                    "metadata_filter": {}
                }
            
            # Use LLM-enhanced filtering
            st.info(f"Calling LLM filter with collection: '{collection_name}'")
            result = self.llm_filter.execute_intelligent_query(collection_name, query, k)
            return result
            
        except Exception as e:
            return {"error": f"LLM-enhanced query failed: {e}"}
    
    def get_collection_status(self, collection_name: str) -> Dict[str, int]:
        """Get status of a collection"""
        try:
            if not self.client:
                return {}
            status = self.client.status.get_status(collection_name=collection_name)
            return {
                "total": status.num_documents,
                "indexed": status.num_indexed_documents,
                "failed": status.num_failed_documents,
                "parsing": status.num_parsing_documents,
                "indexing": status.num_indexing_documents
            }
        except Exception as e:
            return {}

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📚 ZeroEntropy Corpus Manager</h1>', unsafe_allow_html=True)
    
    # Debug information
    st.info(f"🔍 Debug Info:")
    st.info(f"   Current working directory: {os.getcwd()}")
    st.info(f"   Environment file path: {pathlib.Path(__file__).parent / '.env'}")
    st.info(f"   Environment file exists: {(pathlib.Path(__file__).parent / '.env').exists()}")
    st.info(f"   ZEROENTROPY_API_KEY in env: {'ZEROENTROPY_API_KEY' in os.environ}")
    
    # Check if ZeroEntropy is available
    if not ZEROENTROPY_AVAILABLE:
        st.error("ZeroEntropy package not available. Please install it first.")
        return
    
    # Initialize manager
    manager = ZeroEntropyManager()
    if not manager.client:
        st.error("Failed to initialize ZeroEntropy client. Please check your API key.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📁 Collections", "📤 Upload Documents", "💬 Chat Interface"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard(manager)
    elif page == "📁 Collections":
        show_collections(manager)
    elif page == "📤 Upload Documents":
        show_upload_documents(manager)
    elif page == "💬 Chat Interface":
        show_chat_interface(manager)

def show_dashboard(manager: ZeroEntropyManager):
    """Show the main dashboard"""
    st.markdown('<h2 class="section-header">🏠 Dashboard</h2>', unsafe_allow_html=True)
    
    # Get collections
    collections = manager.get_collections()
    
    # Overview cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Collections", len(collections))
    
    with col2:
        total_docs = sum(
            manager.get_collection_status(col).get("total", 0) 
            for col in collections
        )
        st.metric("Total Documents", total_docs)
    
    with col3:
        indexed_docs = sum(
            manager.get_collection_status(col).get("indexed", 0) 
            for col in collections
        )
        st.metric("Indexed Documents", indexed_docs)
    
    with col4:
        failed_docs = sum(
            manager.get_collection_status(col).get("failed", 0) 
            for col in collections
        )
        st.metric("Failed Documents", failed_docs)
    
    # Collections overview
    if collections:
        st.markdown('<h3 class="section-header">📊 Collections Overview</h3>', unsafe_allow_html=True)
        
        collection_data = []
        for col in collections:
            status = manager.get_collection_status(col)
            collection_data.append({
                "Collection": col,
                "Total Documents": status.get("total", 0),
                "Indexed": status.get("indexed", 0),
                "Failed": status.get("failed", 0),
                "Processing": status.get("parsing", 0) + status.get("indexing", 0)
            })
        
        df = pd.DataFrame(collection_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No collections found. Create your first collection to get started!")

def show_collections(manager: ZeroEntropyManager):
    """Show collections management"""
    st.markdown('<h2 class="section-header">📁 Collections Management</h2>', unsafe_allow_html=True)
    
    # Create new collection
    st.markdown("### Create New Collection")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_collection_name = st.text_input(
            "Collection Name",
            placeholder="Enter collection name (e.g., 'research_papers', 'company_docs')"
        )
    
    with col2:
        if st.button("Create Collection", type="primary"):
            if new_collection_name.strip():
                if manager.create_collection(new_collection_name.strip()):
                    st.success(f"Collection '{new_collection_name}' created successfully!")
                    st.rerun()
            else:
                st.error("Please enter a collection name")
    
    # Existing collections
    st.markdown("### Existing Collections")
    collections = manager.get_collections()
    
    if collections:
        for collection in collections:
            with st.expander(f"📁 {collection}", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    status = manager.get_collection_status(collection)
                    st.write(f"**Status:** {status.get('indexed', 0)}/{status.get('total', 0)} documents indexed")
                
                with col2:
                    if status.get('failed', 0) > 0:
                        st.error(f"**Failed:** {status.get('failed', 0)} documents")
                    if status.get('processing', 0) > 0:
                        st.warning(f"**Processing:** {status.get('processing', 0)} documents")
                
                with col3:
                    if st.button(f"Delete {collection}", type="secondary", key=f"del_{collection}"):
                        if manager.delete_collection(collection):
                            st.success(f"Collection '{collection}' deleted successfully!")
                            st.rerun()
    else:
        st.info("No collections found. Create your first collection above!")

def show_upload_documents(manager: ZeroEntropyManager):
    """Show document upload interface"""
    st.markdown('<h2 class="section-header">📤 Upload Documents</h2>', unsafe_allow_html=True)
    
    # Get collections
    collections = manager.get_collections()
    
    if not collections:
        st.warning("No collections available. Please create a collection first.")
        return
    
    # Collection selection
    selected_collection = st.selectbox(
        "Select Collection",
        collections,
        help="Choose the collection where you want to upload documents"
    )
    
    # File upload
    st.markdown("### Upload Files")
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['txt', 'pdf', 'docx', 'csv', 'md'],
        accept_multiple_files=True,
        help="Supported formats: TXT, PDF, DOCX, CSV, MD"
    )
    
    if uploaded_files:
        st.markdown("### Upload Progress")
        
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Determine content type
                file_extension = Path(uploaded_file.name).suffix.lower()
                if file_extension in ['.txt', '.md', '.csv']:
                    content_type = "text"
                else:
                    content_type = "auto"
                
                # Upload to ZeroEntropy
                if manager.upload_document(
                    selected_collection, 
                    temp_path, 
                    content_type,
                    metadata={"source": "streamlit_upload", "filename": uploaded_file.name}
                ):
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                else:
                    st.error(f"❌ Failed to upload {uploaded_file.name}")
                
                # Clean up temp file
                os.remove(temp_path)
        
        st.success("All files processed!")
        st.info("Documents are being indexed. This may take a few moments.")
        
        # Show collection status
        st.markdown("### Collection Status")
        status = manager.get_collection_status(selected_collection)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", status.get("total", 0))
        with col2:
            st.metric("Indexed", status.get("indexed", 0))
        with col3:
            st.metric("Processing", status.get("parsing", 0) + status.get("indexing", 0))
        with col4:
            st.metric("Failed", status.get("failed", 0))

def show_chat_interface(manager: ZeroEntropyManager):
    """Show the chat interface for querying collections"""
    st.markdown('<h2 class="section-header">💬 Chat Interface</h2>', unsafe_allow_html=True)
    
    # Get collections
    collections = manager.get_collections()
    
    if not collections:
        st.warning("No collections available. Please create a collection and upload documents first.")
        return
    
    # Collection selection
    st.info(f"Available collections: {collections}")
    selected_collection = st.selectbox(
        "Select Collection to Query",
        collections,
        help="Choose the collection you want to search"
    )
    st.info(f"Selected collection: '{selected_collection}' (type: {type(selected_collection)})")
    
    # Query type selection
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        query_type = st.selectbox(
            "Query Type",
            ["documents", "pages", "snippets"],
            help="Documents: Full document results, Pages: Page-level results, Snippets: Precise text snippets"
        )
    
    with col2:
        k_results = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of results to return"
        )
    
    with col3:
        st.write("")  # Spacer
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
    
    # LLM-enhanced filtering toggle
    if manager.llm_filter:
        st.markdown("### 🧠 LLM-Enhanced Filtering")
        use_llm_filtering = st.checkbox(
            "Enable intelligent query analysis and metadata filtering",
            value=True,
            help="Uses advanced pattern recognition to understand your queries and apply smart metadata filters"
        )
    else:
        use_llm_filtering = False
        st.info("🧠 LLM-enhanced filtering not available. Install the required dependencies for advanced features.")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat input
    user_query = st.chat_input(
        f"Ask a question about your {selected_collection} collection...",
        key="chat_input"
    )
    
    if user_query:
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query,
            "timestamp": time.time()
        })
        
        # Process query with LLM-enhanced filtering
        with st.spinner("Analyzing query and searching..."):
            st.info(f"🔍 Querying collection: {selected_collection}")
            st.info(f"🔍 Query: {user_query}")
            
            if manager.llm_filter and use_llm_filtering:
                st.info("🧠 Using LLM-enhanced filtering")
                # Use LLM-enhanced filtering
                result = manager.query_collection_llm_enhanced(
                    selected_collection,
                    user_query,
                    k_results
                )
                
                if "error" in result:
                    response_content = f"Error: {result['error']}"
                    st.error(f"LLM query error: {result['error']}")
                else:
                    # Use the LLM-generated response
                    response_content = result['llm_response']
                    
                    # Store additional context for display
                    if 'metadata_filter' in result and result['metadata_filter']:
                        st.info(f"🔍 Applied filters: {json.dumps(result['metadata_filter'], indent=2)}")
            else:
                st.info("🔍 Using basic query (LLM filtering not available)")
                # Fallback to basic query
                results = manager.query_collection(
                    selected_collection,
                    user_query,
                    k_results
                )
                
                # Format response
                if results:
                    response_content = f"Found {len(results)} relevant results:\n\n"
                    
                    for i, result in enumerate(results, 1):
                        if result["type"] == "document":
                            response_content += f"**{i}. Document: {result['path']}**\n"
                            response_content += f"   Relevance Score: {result['score']:.4f}\n"
                            if result.get('metadata'):
                                response_content += f"   Metadata: {result['metadata']}\n"
                        elif result["type"] == "page":
                            response_content += f"**{i}. Page {result['page_index']} from {result['path']}**\n"
                            response_content += f"   Relevance Score: {result['score']:.4f}\n"
                            response_content += f"   Content: {result['content'][:200]}...\n"
                        elif result["type"] == "snippet":
                            response_content += f"**{i}. Snippet from {result['path']}**\n"
                            response_content += f"   Relevance Score: {result['score']:.4f}\n"
                            response_content += f"   Content: {result['content']}\n"
                        response_content += "\n"
                else:
                    response_content = "No relevant results found for your query. Try rephrasing or using different keywords."
        
        # Add assistant response to chat
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": time.time()
        })
    
    # Display chat history
    st.markdown("### Chat History")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
