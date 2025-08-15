"""
Moment - Sports NLP Search
Enhanced Streamlit application with two distinct chat interfaces:
1. Moment Search - Sports-specific metadata filtering
2. ZeroEntropy Native - Full API functionality with search type selection
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
from zeroentropy_api import ZeroEntropyAPI
from typing import Dict, Any

# Try to import the enhanced LLM filter
try:
    from enhanced_llm_filter import EnhancedLLMMetadataFilter
    ENHANCED_FILTER_AVAILABLE = True
except ImportError:
    ENHANCED_FILTER_AVAILABLE = False

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Moment - Sports NLP Search",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Configure OpenAI (using older API format for compatibility)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client (check if modern format is available)
try:
    # Debug: Show OpenAI version
    st.session_state.openai_version = getattr(openai, '__version__', 'Unknown')
    
    # Try modern format first
    if hasattr(openai, 'OpenAI'):
        try:
            # Test if we can actually create the client
            openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            st.session_state.openai_available = True
            st.session_state.openai_modern = True
            st.session_state.openai_debug = f"Modern API detected (v{st.session_state.openai_version})"
        except Exception as client_error:
            # Modern API failed, fallback to legacy
            openai_client = None
            st.session_state.openai_available = True
            st.session_state.openai_modern = False
            st.session_state.openai_debug = f"Modern API failed: {client_error}, using Legacy"
    else:
        # Fallback to older format
        openai_client = None
        st.session_state.openai_available = True
        st.session_state.openai_modern = False
        st.session_state.openai_debug = f"Legacy API detected (v{st.session_state.openai_version})"
except Exception as e:
    openai_client = None
    st.session_state.openai_available = False
    st.session_state.openai_modern = False
    st.session_state.openai_debug = f"Error initializing: {e}"
    st.warning(f"OpenAI client not available: {e}")

# Initialize ZeroEntropy API client
try:
    zeroentropy_api = ZeroEntropyAPI()
    st.session_state.zeroentropy_available = True
except Exception as e:
    st.session_state.zeroentropy_available = False
    st.error(f"ZeroEntropy API not available: {e}")

# Function definitions (moved to top to avoid "not defined" errors)
def process_gpt5_query(prompt: str) -> str:
    """Process GPT-5 enhanced query with proper metadata filtering"""
    if not st.session_state.current_collection:
        return "❌ No collection selected. Please select a collection from the sidebar."
    
    if not st.session_state.openai_available:
        return "❌ OpenAI client not available. Please check your API key and try again."
    
    if not ENHANCED_FILTER_AVAILABLE:
        st.error("❌ **Enhanced LLM Filter not available** - using basic search")
        # Fallback to basic search
        search_results = zeroentropy_api.search_documents(
            collection_name=st.session_state.current_collection,
            query=prompt,
            k=50,
            include_metadata=True
        )
        return format_gpt5_results(search_results, prompt, "Basic search (fallback)", None)
    
    try:
        # Initialize the enhanced filter
        llm_filter = EnhancedLLMMetadataFilter()
        
        # Try GPT interpretation first
        gpt_interpretation = llm_filter.interpret_query_with_gpt(prompt)
        
        if "error" not in gpt_interpretation:
            # Use GPT interpretation
            metadata_filter = gpt_interpretation.get("metadata_filter", {})
            query_type = gpt_interpretation.get("query_type", "semantic")
            intent = gpt_interpretation.get("intent", "")
            explanation = gpt_interpretation.get("explanation", "")
            
            st.success(f"🔍 **GPT-5 Enhanced Query**: {intent}")
            st.info(f"🎯 **Query Type**: {query_type}")
            
            if metadata_filter and query_type == "filtered":
                st.info(f"🔧 **Applied Metadata Filter**: {json.dumps(metadata_filter, indent=2)}")
                st.info(f"💡 **Filter Explanation**: {explanation}")
                
                # Execute search with metadata filter
                search_results = zeroentropy_api.search_documents(
                    collection_name=st.session_state.current_collection,
                    query=prompt,
                    k=50,
                    include_metadata=True,
                    filter_dict=metadata_filter
                )
                
                return format_gpt5_results(search_results, prompt, intent, metadata_filter)
            else:
                # Semantic search without filters
                st.info("💡 **Using semantic search** (no specific filters applied)")
                search_results = zeroentropy_api.search_documents(
                    collection_name=st.session_state.current_collection,
                    query=prompt,
                    k=50,
                    include_metadata=True
                )
                
                return format_gpt5_results(search_results, prompt, intent, None)
                
        else:
            # GPT failed, use fallback pattern matching
            st.warning(f"⚠️ **GPT interpretation failed**: {gpt_interpretation['error']}")
            st.info("🔄 **Using fallback pattern matching...**")
            
            fallback_result = llm_filter.analyze_query_and_create_filter(prompt)
            metadata_filter = fallback_result.get("metadata_filter", {})
            intent = fallback_result.get("intent", "")
            explanation = fallback_result.get("explanation", "")
            
            st.info(f"🔍 **Fallback Analysis**: {intent}")
            
            if metadata_filter:
                st.info(f"🔧 **Applied Metadata Filter**: {json.dumps(metadata_filter, indent=2)}")
                st.info(f"💡 **Filter Explanation**: {explanation}")
                
                # Execute search with fallback filter
                search_results = zeroentropy_api.search_documents(
                    collection_name=st.session_state.current_collection,
                    query=prompt,
                    k=50,
                    include_metadata=True,
                    filter_dict=metadata_filter
                )
                
                return format_gpt5_results(search_results, prompt, intent, metadata_filter)
            else:
                # No filters, basic search
                st.info("💡 **No filters detected** - using basic search")
                search_results = zeroentropy_api.search_documents(
                    collection_name=st.session_state.current_collection,
                    query=prompt,
                    k=50,
                    include_metadata=True
                )
                
                return format_gpt5_results(search_results, prompt, intent, None)
        
    except Exception as e:
        st.error(f"❌ **Error**: {str(e)}")
        # Fallback to basic search
        search_results = zeroentropy_api.search_documents(
            collection_name=st.session_state.current_collection,
            query=prompt,
            k=50,
            include_metadata=True
        )
        return format_gpt5_results(search_results, prompt, "Basic search (fallback)", None)

def process_zeroentropy_query(query: str, search_type: str, results_per_page: int, latency_mode: str) -> str:
    """Process ZeroEntropy native search query with smart pagination support"""
    try:
        if not st.session_state.current_collection:
            return "❌ No collection selected. Please select a collection from the sidebar."
        
        # Get current page for pagination
        current_page = st.session_state.get('current_page', 0)
        
        # For pagination, we need to request more results than we show per page
        # This allows us to simulate pagination through the results
        total_requested = max(results_per_page * 3, 50)  # Request at least 3 pages worth or 50 results
        
        # Execute search based on selected type with larger result set
        if search_type == "top-documents":
            search_results = zeroentropy_api.search_documents(
                collection_name=st.session_state.current_collection,
                query=query,
                k=total_requested,
                include_metadata=True
            )
            return format_native_results_with_pagination(search_results, query, "Documents", search_type, current_page, results_per_page, total_requested)
            
        elif search_type == "top-pages":
            search_results = zeroentropy_api.search_pages(
                collection_name=st.session_state.current_collection,
                query=query,
                k=total_requested,
                include_content=True,
                latency_mode=latency_mode
            )
            return format_native_results_with_pagination(search_results, query, "Pages", search_type, current_page, results_per_page, total_requested)
            
        elif search_type == "top-snippets-coarse":
            search_results = zeroentropy_api.search_snippets(
                collection_name=st.session_state.current_collection,
                query=query,
                k=total_requested,
                precise_responses=False,
                include_document_metadata=True
            )
            return format_native_results_with_pagination(search_results, query, "Coarse Snippets", search_type, current_page, results_per_page, total_requested)
            
        elif search_type == "top-snippets-fine":
            search_results = zeroentropy_api.search_snippets(
                collection_name=st.session_state.current_collection,
                query=query,
                k=total_requested,
                precise_responses=True,
                include_document_metadata=True
            )
            return format_native_results_with_pagination(search_results, query, "Fine Snippets", search_type, current_page, results_per_page, total_requested)
            
    except Exception as e:
        return f"❌ Error processing ZeroEntropy query: {str(e)}"

# Simple helper functions for the simplified approach
def get_smart_date_context():
    """Get current date context - simplified"""
    from datetime import datetime
    today = datetime.now()
    return {
        "today": today.strftime("%Y-%m-%d"),
        "current_month": today.strftime("%Y-%m")
    }

def detect_query_patterns(prompt: str) -> Dict:
    """Detect query patterns - simplified"""
    patterns = {}
    prompt_lower = prompt.lower()
    
    if "september" in prompt_lower or "2024" in prompt_lower:
        patterns["time_period"] = "date_specific"
    if "vs" in prompt_lower or "versus" in prompt_lower:
        patterns["head_to_head"] = True
    if "stadium" in prompt_lower or "venue" in prompt_lower:
        patterns["venue_specific"] = True
        
    return patterns

# Remove unused complex functions
# def build_intelligent_filter(intent: str, patterns: Dict, extracted_filters: Dict) -> Dict:
#     """Build intelligent filters based on detected patterns and extracted information"""
#     # This function is no longer used with the simplified approach
#     pass

# def build_sports_metadata_filter(venue=None, team=None, date=None, player=None):
#     """Build metadata filter for sports data based on extracted information"""
#     # This function is no longer used with the simplified approach
#     pass

# def create_clean_date_filter_isolated(month: int, year: str = "2024") -> dict:
#     """Create a clean date filter completely isolated from Streamlit to avoid corruption"""
#     # This function is no longer used with the simplified approach
#     pass

# def execute_zeroentropy_search_without_streamlit(collection_name: str, query: str, metadata_filter: Dict, k: int = 50) -> Dict[str, Any]:
#     """Execute ZeroEntropy search without any Streamlit involvement to avoid corruption issues"""
#     # This function is no longer used with the simplified approach
#     pass

def format_gpt5_results(results: dict, query: str, interpretation: str, filters: dict) -> str:
    """Format Moment search results"""
    # Handle both 'results' and 'documents' response formats
    if "results" in results:
        items = results["results"]
    elif "documents" in results:
        items = results["documents"]
    else:
        items = []
    
    if not items:
        return f"""
        🔍 **Query Analysis**: {query}
        
        🤖 **GPT Interpretation**: {interpretation}
        
        📊 **Total Results**: 0
        
        🎯 **Query Analysis**: {query}
        📊 No documents found
        
        🔍 **Applied Filters**: {json.dumps(json.loads(json.dumps(filters)), indent=2) if filters else 'None'}
        
        ❌ **No documents match these criteria**
        
        💡 **Suggestions**:
        • Try broadening your search criteria
        • Remove date filters to search all available data
        • Search for specific teams or venues instead
        """
    
    # Format results
    formatted_results = []
    for i, doc in enumerate(items, 1):
        metadata = doc.get("metadata", {})
        venue = metadata.get("venue", "N/A") if metadata else "N/A"
        team = metadata.get("team", "N/A") if metadata else "N/A"
        date = metadata.get("date", "N/A") if metadata else "N/A"
        
        formatted_results.append(f"""
        **{i}. {doc.get('path', 'Unknown Document')}**
        📍 **Venue**: {venue}
        🏟️ **Team**: {team}
        📅 **Date**: {date}
        📊 **Score**: {doc.get('score', 'N/A')}
        📝 **Path**: {doc.get('path', 'No path available')}
        """)
    
    return f"""
    🔍 **Query Analysis**: {query}
    
    🤖 **GPT Interpretation**: {interpretation}
    
    📊 **Total Results**: {len(items)}
    
    🎯 **Query Analysis**: {query}
    📊 **Found {len(items)} documents**
    
    🔍 **Applied Filters**: {json.dumps(json.loads(json.dumps(filters)), indent=2) if filters else 'None'}
    
    ---
    
    **📋 Results:**
    {''.join(formatted_results)}
    """

def format_native_results_with_pagination(results: dict, query: str, result_type: str, search_type: str, current_page: int, results_per_page: int, total_requested: int) -> str:
    """Format native ZeroEntropy search results with smart pagination support"""
    if "error" in results:
        return f"❌ **{result_type} Search Failed**: {results.get('error')}"
    
    # Get the appropriate results key based on search type and API response format
    if search_type == "top-documents":
        items = results.get("results", results.get("documents", []))
    elif search_type == "top-pages":
        items = results.get("results", results.get("pages", []))
    elif search_type in ["top-snippets-coarse", "top-snippets-fine"]:
        items = results.get("results", results.get("snippets", []))
    else:
        items = []
    
    # Update session state for pagination
    st.session_state.total_results = len(items) if items else 0
    st.session_state.last_search_query = query
    st.session_state.last_search_type = search_type
    st.session_state.last_results_per_page = results_per_page
    
    if not items:
        return f"""
        🔍 **{result_type} Search**: {query}
        📊 **Total Results**: 0
        ❌ **No {result_type.lower()} found**
        """
    
    # Calculate the start and end indices for the current page
    start_idx = current_page * results_per_page
    end_idx = min(start_idx + results_per_page, len(items))
    
    # Get only the items for the current page
    page_items = items[start_idx:end_idx]
    
    # Format results for current page only
    formatted_results = []
    for i, item in enumerate(page_items):
        # Calculate the global result number (1-based for display)
        global_result_num = start_idx + i + 1
        
        if search_type == "top-documents":
            metadata = item.get("metadata", {})
            venue = metadata.get("venue", "N/A") if metadata else "N/A"
            team = metadata.get("team", "N/A") if metadata else "N/A"
            date = metadata.get("date", "N/A") if metadata else "N/A"
            
            formatted_results.append(f"""
            **{global_result_num}. {item.get('path', 'Unknown Document')}**
            📍 **Venue**: {venue}
            🏟️ **Team**: {team}
            📅 **Date**: {date}
            📊 **Score**: {item.get('score', 'N/A')}
            📝 **Path**: {item.get('path', 'No path available')}
            """)
            
        elif search_type == "top-pages":
            formatted_results.append(f"""
            **{global_result_num}. Page {item.get('page_index', 'N/A')}**
            📄 **Document**: {item.get('path', 'Unknown')}
            📊 **Score**: {item.get('score', 'N/A')}
            """)
            
        elif search_type in ["top-snippets-coarse", "top-snippets-fine"]:
            precision = "Fine" if search_type == "top-snippets-fine" else "Coarse"
            formatted_results.append(f"""
            **{global_result_num}. {precision} Snippet**
            📄 **Document**: {item.get('path', 'Unknown')}
            📊 **Score**: {item.get('score', 'N/A')}
            """)
    
    return f"""
    🔍 **{result_type} Search**: {query}
    📊 **Total Results**: {len(items)}
    📄 **Showing**: Results {start_idx + 1}-{end_idx} of {len(items)}
    🎯 **Search Type**: {search_type.replace('-', ' ').title()}
    📍 **Current Page**: {current_page + 1}
    🔧 **Results per Page**: {results_per_page}
    
    ---
    
    **📋 Results (Page {current_page + 1}):**
    {''.join(formatted_results)}
    """

# Custom CSS for dual chat interface
st.markdown("""
<style>
    /* Main layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Collection status metric */
    .collection-status {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #34495e;
        margin-bottom: 2rem;
    }
    
    /* Collection cards */
    .collection-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .collection-card:hover {
        transform: translateY(-2px);
    }
    
    /* Chat styling */
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stChatMessage[data-testid="chat_message_user"] {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .stChatMessage[data-testid="chat_message_assistant"] {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    /* Search mode selector */
    .search-mode-selector {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Results container */
    .results-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Sticky parameters section */
    .sticky-params {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #007bff;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .sticky-params h4 {
        margin: 0;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    
    /* Alternative: Fixed position for better visibility */
    .fixed-params {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #007bff;
    }
    
    .sticky-params .stMarkdown {
        margin-bottom: 0.5rem;
    }
    
    /* Parameter controls styling */
    .param-controls {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #dee2e6;
    }
    
    /* Pagination styling */
    .pagination-info {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "native_messages" not in st.session_state:
    st.session_state.native_messages = []
if "current_collection" not in st.session_state:
    st.session_state.current_collection = None
if "zeroentropy_available" not in st.session_state:
    st.session_state.zeroentropy_available = True
if "openai_available" not in st.session_state:
    st.session_state.openai_available = False
if "openai_modern" not in st.session_state:
    st.session_state.openai_modern = False
if "openai_version" not in st.session_state:
    st.session_state.openai_version = "Unknown"
if "openai_debug" not in st.session_state:
    st.session_state.openai_debug = "Unknown"
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "total_results" not in st.session_state:
    st.session_state.total_results = 0
if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""
if "last_search_type" not in st.session_state:
    st.session_state.last_search_type = ""
if "last_results_per_page" not in st.session_state:
    st.session_state.last_results_per_page = 20
if "doc_to_delete" not in st.session_state:
    st.session_state.doc_to_delete = None
if "show_delete_doc_confirm" not in st.session_state:
    st.session_state.show_delete_doc_confirm = False
if "show_delete_collection_confirm" not in st.session_state:
    st.session_state.show_delete_collection_confirm = False

# Sidebar
with st.sidebar:
    st.header("⚽ Moment Sports Search")
    
    # Collection Management
    st.subheader("📚 Collection Management")
    
    # Create new collection
    new_collection = st.text_input("Create New Collection", key="new_collection_input")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("➕ Create Collection", key="create_collection_btn"):
            if new_collection.strip():
                try:
                    result = zeroentropy_api.add_collection(new_collection.strip())
                    if "error" not in result:
                        st.success(f"✅ Collection '{new_collection.strip()}' created successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create collection: {result.get('error')}")
                except Exception as e:
                    st.error(f"❌ Error creating collection: {e}")
            else:
                st.warning("⚠️ Please enter a collection name")
    
    with col2:
        if st.button("🗑️ Delete Collection", key="delete_collection_btn", type="secondary"):
            if st.session_state.current_collection:
                st.session_state.show_delete_collection_confirm = True
            else:
                st.warning("⚠️ Please select a collection to delete")
    
    # Delete collection confirmation
    if st.session_state.get('show_delete_collection_confirm', False) and st.session_state.current_collection:
        st.warning("⚠️ **Delete Collection Confirmation**")
        st.error(f"🗑️ You are about to delete collection: **{st.session_state.current_collection}**")
        st.error("❌ **This action cannot be undone!**")
        st.error("📄 **All documents in this collection will be permanently deleted!**")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ **YES, DELETE**", key="confirm_delete_collection", type="primary"):
                try:
                    with st.spinner("🗑️ Deleting collection..."):
                        result = zeroentropy_api.delete_collection(st.session_state.current_collection)
                        if "error" not in result:
                            st.success(f"✅ Collection '{st.session_state.current_collection}' deleted successfully!")
                            st.session_state.current_collection = None
                            st.session_state.show_delete_collection_confirm = False
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to delete collection: {result.get('error')}")
                except Exception as e:
                    st.error(f"❌ Error deleting collection: {e}")
        
        with col2:
            if st.button("❌ **CANCEL**", key="cancel_delete_collection", type="secondary"):
                st.session_state.show_delete_collection_confirm = False
                st.rerun()
        
        # Prevent the confirmation from disappearing by adding a persistent element
        st.markdown("---")
        st.info("💡 **Confirmation Required**: Click YES to delete or CANCEL to abort")
    
    # Select Collection
    if st.session_state.zeroentropy_available:
        try:
            collections_response = zeroentropy_api.get_collection_list()
            
            if "collection_names" in collections_response and collections_response["collection_names"]:
                collection_names = collections_response["collection_names"]
                # Ensure we have a valid index
                default_index = 0 if collection_names else None
                selected_collection = st.selectbox(
                    "Select Collection",
                    collection_names,
                    index=default_index,
                    key="collection_selector"
                )
                if selected_collection and selected_collection != st.session_state.current_collection:
                    st.session_state.current_collection = selected_collection
                    st.rerun()
            elif "collections" in collections_response and collections_response["collections"]:
                # Fallback for different API response format
                collection_names = [col["name"] for col in collections_response["collections"]]
                # Ensure we have a valid index
                default_index = 0 if collection_names else None
                selected_collection = st.selectbox(
                    "Select Collection",
                    collection_names,
                    index=default_index,
                    key="collection_selector"
                )
                if selected_collection and selected_collection != st.session_state.current_collection:
                    st.session_state.current_collection = selected_collection
                    st.rerun()
            else:
                st.info("📚 No collections found. Create your first collection using the form above!")
        except Exception as e:
            st.error(f"Error loading collections: {e}")
            st.info("📚 No collections available. Create your first collection!")
    
    # Collection Status
    if st.session_state.current_collection:
        st.subheader("📊 Collection Status")
        try:
            status = zeroentropy_api.get_collection_status(st.session_state.current_collection)
            if "error" not in status:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current", st.session_state.current_collection)
                with col2:
                    # Handle different status response formats
                    if "num_documents" in status:
                        st.metric("Documents", status.get("num_documents", 0))
                    elif "document_count" in status:
                        st.metric("Documents", status.get("document_count", 0))
                    else:
                        st.metric("Documents", "N/A")
                
                # Show additional status info if available
                if "status" in status:
                    st.info(f"Status: {status['status']}")
                if "last_updated" in status:
                    st.info(f"Last Updated: {status['last_updated']}")
            else:
                st.error(f"Status error: {status.get('error')}")
        except Exception as e:
            st.error(f"Error getting status: {e}")
    
    # Document Upload & Management
    with st.expander("📁 Document Upload & Management"):
        if st.session_state.current_collection:
            # Document list
            st.subheader("📄 Documents in Collection")
            try:
                documents = zeroentropy_api.get_document_list(st.session_state.current_collection)
                if "error" not in documents and documents.get("documents"):
                    st.info(f"📊 **Total Documents**: {len(documents['documents'])}")
                    
                    for i, doc in enumerate(documents["documents"]):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"**{i+1}.** {doc.get('path', 'Unknown')}")
                        with col2:
                            st.write(f"📅 {doc.get('last_modified', 'Unknown')}")
                        with col3:
                            if st.button(f"🗑️", key=f"delete_doc_{i}", help=f"Delete {doc.get('path', 'Unknown')}"):
                                st.session_state.doc_to_delete = doc.get('path', 'Unknown')
                                st.session_state.show_delete_doc_confirm = True
                                st.rerun()
                else:
                    st.info("📭 **No documents found** in this collection")
            except Exception as e:
                st.warning(f"⚠️ Could not fetch documents: {e}")
            
            # Delete document confirmation
            if st.session_state.get('show_delete_doc_confirm', False) and st.session_state.get('doc_to_delete'):
                st.warning("⚠️ **Delete Document Confirmation**")
                st.error(f"🗑️ You are about to delete document: **{st.session_state.doc_to_delete}**")
                st.error("❌ **This action cannot be undone!**")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ **YES, DELETE**", key="confirm_delete_doc", type="primary"):
                        try:
                            with st.spinner("🗑️ Deleting document..."):
                                result = zeroentropy_api.delete_document(
                                    st.session_state.current_collection, 
                                    st.session_state.doc_to_delete
                                )
                                if "error" not in result:
                                    st.success(f"✅ Document '{st.session_state.doc_to_delete}' deleted successfully!")
                                    st.session_state.show_delete_doc_confirm = False
                                    st.session_state.doc_to_delete = None
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to delete document: {result.get('error')}")
                        except Exception as e:
                            st.error(f"❌ Error deleting document: {e}")
                
                with col2:
                    if st.button("❌ **CANCEL**", key="cancel_delete_doc", type="secondary"):
                        st.session_state.show_delete_doc_confirm = False
                        st.session_state.doc_to_delete = None
                        st.rerun()
                
                # Prevent the confirmation from disappearing by adding a persistent element
                st.markdown("---")
                st.info("💡 **Confirmation Required**: Click YES to delete or CANCEL to abort")
            
            st.markdown("---")
            
            # Upload new document
            st.subheader("📤 Upload New Document")
            uploaded_file = st.file_uploader(
                "Upload CSV, Text, or Requirements File",
                type=['csv', 'txt', 'py', 'md', 'json', 'yml', 'yaml'],
                key="file_uploader"
            )
            
            if uploaded_file:
                st.info(f"📄 **File**: {uploaded_file.name}")
                st.info(f"📊 **Size**: {uploaded_file.size} bytes")
                st.info(f"🔤 **Type**: {uploaded_file.type}")
                
                # Show file preview
                try:
                    if uploaded_file.type == "text/csv":
                        import pandas as pd
                        df = pd.read_csv(uploaded_file)
                        st.info(f"📊 **CSV Preview**: {len(df)} rows, {len(df.columns)} columns")
                        st.dataframe(df.head(3))
                    else:
                        content = uploaded_file.getvalue().decode('utf-8')
                        st.info(f"📝 **Text Preview**: {len(content)} characters")
                        with st.expander("📄 **File Content Preview**"):
                            st.code(content[:500] + ("..." if len(content) > 500 else ""))
                except Exception as e:
                    st.warning(f"⚠️ Could not preview file: {e}")
                
                if st.button("🚀 Upload Document"):
                    try:
                        with st.spinner("📤 Uploading document..."):
                            # Read file content based on type
                            if uploaded_file.type == "text/csv":
                                import pandas as pd
                                df = pd.read_csv(uploaded_file)
                                content = df.to_csv(index=False)
                                file_type = "csv"
                            else:
                                content = uploaded_file.getvalue().decode('utf-8')
                                file_type = "text"
                            
                            # Create appropriate metadata
                            metadata = {
                                "source": "streamlit_upload",
                                "filename": uploaded_file.name,
                                "file_type": file_type,
                                "uploaded_at": datetime.now().isoformat()
                            }
                            
                            # Add sports-specific metadata for CSV files
                            if file_type == "csv":
                                metadata.update({
                                    "type": "sports_data",
                                    "rows": len(df) if 'df' in locals() else 0,
                                    "columns": len(df.columns) if 'df' in locals() else 0
                                })
                            
                            st.info(f"📋 **Preparing upload with metadata**:")
                            st.json(metadata)
                            
                            # Upload to ZeroEntropy using the appropriate method
                            if file_type == "csv":
                                result = zeroentropy_api.upload_csv_content(
                                    collection_name=st.session_state.current_collection,
                                    file_path=uploaded_file.name,
                                    content=content,
                                    metadata=metadata
                                )
                            else:
                                # For text files, use add_text_document
                                result = zeroentropy_api.add_text_document(
                                    collection_name=st.session_state.current_collection,
                                    path=uploaded_file.name,
                                    text_content=content,
                                    metadata=metadata
                                )
                            
                            if "error" not in result:
                                st.success(f"✅ **Document '{uploaded_file.name}' uploaded successfully!**")
                                st.info(f"📋 **Result**: {result.get('message', 'Upload completed')}")
                                
                                # Show collection status update
                                try:
                                    status = zeroentropy_api.get_collection_status(st.session_state.current_collection)
                                    if "error" not in status:
                                        st.success(f"📚 **Collection Status**: {status.get('status', 'Unknown')}")
                                        if "document_count" in status:
                                            st.info(f"📊 **Total Documents**: {status.get('document_count', 'Unknown')}")
                                except Exception as e:
                                    st.warning(f"⚠️ Could not fetch updated collection status: {e}")
                                
                                # Refresh the app
                                st.rerun()
                            else:
                                st.error(f"❌ **Upload failed**: {result.get('error')}")
                                st.error(f"🔍 **Status Code**: {result.get('status_code', 'Unknown')}")
                                
                                # Show troubleshooting tips
                                st.info("💡 **Troubleshooting Tips**:")
                                st.info("   • Check your ZeroEntropy API key")
                                st.info("   • Ensure the collection exists")
                                st.info("   • Try with a smaller file")
                                st.info("   • Check file format compatibility")
                                
                                # Show debug info
                                with st.expander("🔍 **Debug Information**"):
                                    st.json(result)
                                
                    except Exception as e:
                        st.error(f"❌ **Error uploading document**: {str(e)}")
                        st.error(f"🔍 **Error Type**: {type(e).__name__}")
                        
                        # Show detailed error info
                        import traceback
                        with st.expander("🔍 **Error Details**"):
                            st.code(traceback.format_exc())
        else:
            st.info("👈 **Select a collection first** to upload documents")
            st.info("💡 **Tip**: Use the sidebar to select or create a collection")

# Main content area
st.title("Moment - Sports NLP Search")
st.markdown("---")

if st.session_state.current_collection and st.session_state.show_delete_collection_confirm:
    st.session_state.show_delete_collection_confirm = False
    st.rerun()

if st.session_state.current_collection:
    # Collection info
    st.subheader(f"📚 Collection: {st.session_state.current_collection}")
    
    # Search mode selector
    search_mode = st.selectbox(
        "🔍 Choose Search Mode",
        options=[
            "🤖 Moment Search",
            "⚡ ZeroEntropy Native Search"
        ],
        help="Moment: AI-powered sports filtering | Native: Direct API calls"
    )
    
    if search_mode == "🤖 Moment Search":
        # Moment Search Interface
        st.markdown("### 🤖 Moment Search")
        # Display Moment chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input for Moment
        if prompt := st.chat_input("Ask me anything about your documents..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 Analyzing..."):
                    response = process_gpt5_query(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
    else:
        # ZeroEntropy Native Search Interface
        st.markdown("### ⚡ ZeroEntropy API")
        st.markdown("Direct access to all ZeroEntropy API capabilities.")
        
        # Sticky search parameters container
        st.markdown("""
        <div class="sticky-params">
            <h4>🔧 Search Parameters</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Search parameters in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            search_type = st.selectbox(
                "Search Type",
                options=[
                    "top-documents",
                    "top-pages", 
                    "top-snippets-coarse",
                    "top-snippets-fine"
                ],
                help="Choose the type of search results"
            )
        
        with col2:
            results_per_page = st.slider("Results per page", 1, 50, 20)
        
        with col3:
            latency_mode = st.selectbox(
                "Latency Mode",
                options=["low", "medium", "high"],
                help="Balance between speed and accuracy"
            )
        
        # Search input and button
        st.markdown("---")
        st.markdown("**🔍 Search Query**")
        
        # Search input with Enter key support
        search_query = st.text_input(
            "Enter your search query... (Press Enter to search)", 
            key="native_search_input"
        )
        
        # Handle search when Enter is pressed or query changes
        if search_query and search_query != st.session_state.get('last_search_query', ""):
            # Always reset pagination for new searches to start fresh
            st.session_state.current_page = 0
            
            st.session_state.last_search_query = search_query
            st.session_state.last_search_type = search_type
            st.session_state.last_results_per_page = results_per_page
            
            st.session_state.native_messages.append({"role": "user", "content": search_query})
            st.rerun()
        
        # Pagination controls
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if "current_page" not in st.session_state:
                st.session_state.current_page = 0
            if "last_search_query" not in st.session_state:
                st.session_state.last_search_query = ""
            if "last_search_type" not in st.session_state:
                st.session_state.last_search_type = ""
            if "last_results_per_page" not in st.session_state:
                st.session_state.last_results_per_page = 20
            
            # Show current page status
            if st.session_state.last_search_query:
                st.info(f"**Page {st.session_state.current_page + 1}**")
            else:
                st.info("**Ready to Search**")
        
        with col2:
            # Only enable previous if we have a previous page and last search
            can_go_previous = (st.session_state.current_page > 0 and 
                              st.session_state.last_search_query and 
                              st.session_state.last_search_type)
            
            if st.button("⬅️ Previous Page", disabled=not can_go_previous):
                st.session_state.current_page -= 1
                # Re-run the last search with new page
                st.rerun()
        
        with col3:
            # Only enable next if we have results and last search
            can_go_next = (st.session_state.total_results > 0 and 
                          st.session_state.last_search_query and 
                          st.session_state.last_search_type and
                          (st.session_state.current_page + 1) * st.session_state.last_results_per_page < st.session_state.total_results)
            
            if st.button("➡️ Next Page", disabled=not can_go_next):
                st.session_state.current_page += 1
                # Re-run the last search with new page
                st.rerun()
        
        with col4:
            if st.button("🔄 Reset to Page 1"):
                st.session_state.current_page = 0
                st.rerun()
        
        # Show pagination info and status
        if st.session_state.last_search_query and st.session_state.last_search_type:
            if st.session_state.total_results > 0:
                total_pages = (st.session_state.total_results + st.session_state.last_results_per_page - 1) // st.session_state.last_results_per_page
                current_start = st.session_state.current_page * st.session_state.last_results_per_page + 1
                current_end = min((st.session_state.current_page + 1) * st.session_state.last_results_per_page, st.session_state.total_results)
                
                st.info(f"**Showing {current_start}-{current_end} of {st.session_state.total_results} results** (Page {st.session_state.current_page + 1} of {total_pages})")
                
                # Show pagination hint
                if st.session_state.total_results >= 50:  # If we have many results
                    st.info("💡 **Tip**: Set 'Results per page' higher to see more results at once, or use pagination to browse through all results.")
                
                # Show navigation status
                if st.session_state.current_page > 0:
                    st.success(f"✅ **Previous Page Available** - Click '⬅️ Previous Page' to go back")
                if can_go_next:
                    st.success(f"✅ **Next Page Available** - Click '➡️ Next Page' to see more results")
                else:
                    st.info(f"🏁 **End of Results** - You've reached the last page")
            else:
                st.info("🔍 **Search completed** - No results found")
        else:
            st.info("💡 **Ready to search** - Enter a query above to get started")
        
        # Display search history
        if st.session_state.native_messages:
            st.markdown("---")
            st.markdown("**📋 Search History**")
            for msg in st.session_state.native_messages[-3:]:  # Show last 3 searches
                if msg["role"] == "user":
                    st.text(msg["content"])
        
        # Display search results if we have a last search
        if st.session_state.last_search_query and st.session_state.last_search_type:
            st.markdown("---")
            st.markdown("**🔍 Search Results**")
            
            # Process and display the search results
            with st.spinner("⚡ Searching with ZeroEntropy..."):
                # Execute search using the simplified approach
                st.info("🔍 **Debug**: Executing search with simplified approach...")
                
                try:
                    search_results = zeroentropy_api.search_documents(
                        collection_name=st.session_state.current_collection,
                        query=search_query,
                        k=50,
                        include_metadata=True
                    )
                    
                    # Display the results
                    response = format_gpt5_results(search_results, search_query, search_query, None)
                    st.markdown(response)
                    
                    # Add to messages if not already there
                    if not any(msg.get("content") == response for msg in st.session_state.native_messages):
                        st.session_state.native_messages.append({"role": "assistant", "content": response})
                        
                except Exception as e:
                    error_msg = f"❌ **Search Error**: {str(e)}"
                    st.error(error_msg)
                    
                    # Add error to messages
                    if not any(msg.get("content") == error_msg for msg in st.session_state.native_messages):
                        st.session_state.native_messages.append({"role": "assistant", "content": error_msg})
    
else:
    # Welcome screen when no collection is selected
    st.markdown("""
    # 🏟️ Welcome to Moment - Sports NLP Search
    
    ## 🚀 Get Started
    
    1. **Select a Collection** from the sidebar to begin searching
    2. **Choose Your Search Mode**:
       - 🤖 **Moment Search**: AI-powered sports filtering
       - ⚡ **Native**: Direct ZeroEntropy API access
    3. **Start Searching** your sports documents!
    
    ## 📚 Available Collections
    
    Use the sidebar to select from your available collections and start exploring your sports data.
    """)
