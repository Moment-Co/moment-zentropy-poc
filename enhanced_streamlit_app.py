#!/usr/bin/env python3
"""
Enhanced Moment - Sports NLP Search Streamlit Application
Features GPT-5 integration, intelligent metadata filtering, and professional UI
"""

import streamlit as st
import os
import tempfile
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Import our custom modules
try:
    from enhanced_llm_filter import EnhancedLLMMetadataFilter
    from llm_metadata_filter import LLMMetadataFilter
    ENHANCED_AVAILABLE = True
except ImportError as e:
    st.error(f"Enhanced LLM filter not available: {e}")
    ENHANCED_AVAILABLE = False

try:
    from zeroentropy import ZeroEntropy, ConflictError, APIStatusError
    ZEROENTROPY_AVAILABLE = True
except ImportError as e:
    st.error(f"Moment - Sports NLP Search not available: {e}")
    ZEROENTROPY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Moment - AI-Powered Sports Search",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS to hide warnings and improve UI
st.markdown("""
<style>
    .stAlert {
        display: none;
    }
    .stDeployButton {
        display: none;
    }
    
    /* Centered chat interface like ChatGPT */
    .main .block-container {
        max-width: 800px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    .stChatMessage[data-testid="chatMessage"] {
        margin: 1rem 0 !important;
    }
    
    /* User message styling */
    .stChatMessage[data-testid="chatMessage"] .stChatMessageContent {
        background: #007AFF !important;
        color: white !important;
        border-radius: 18px !important;
        padding: 0.75rem 1rem !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 80% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="chatMessage"] .stChatMessageContent {
        background: #f1f1f1 !important;
        color: #333 !important;
        border-radius: 18px !important;
        padding: 0.75rem 1rem !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        max-width: 80% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        position: fixed !important;
        bottom: 2rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 600px !important;
        max-width: 90vw !important;
        z-index: 1000 !important;
        background: white !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Chat input focus styling */
    .stChatInput:focus-within {
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        border-color: #007AFF !important;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background: #f8f9fa !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    
    /* Sidebar section styling */
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Button improvements */
    .stButton > button {
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* Welcome screen styling */
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .get-started-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Collection cards */
    .collection-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Status metrics */
    .status-metric {
        background: white;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    /* Smooth transitions */
    * {
        transition: all 0.2s ease;
    }
    
    /* Loading spinner improvements */
    .stSpinner > div {
        border-color: #007AFF !important;
    }
    
    /* Success/error message styling */
    .stSuccess {
        background: #d4edda !important;
        border-color: #c3e6cb !important;
        color: #155724 !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background: #f8d7da !important;
        border-color: #f5c6cb !important;
        color: #721c24 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_search_client():
    """Initialize search client"""
    if not ZEROENTROPY_AVAILABLE:
        return None
    
    api_key = os.getenv("ZEROENTROPY_API_KEY")
    if not api_key:
        st.error("❌ MOMENT_SPORTS_NLP_API_KEY not found in .env file")
        return None
    
    try:
        client = ZeroEntropy()
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize search client: {e}")
        return None

def initialize_llm_filters():
    """Initialize LLM filters"""
    if not ENHANCED_AVAILABLE:
        return None, None
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    try:
        enhanced_filter = EnhancedLLMMetadataFilter(openai_api_key=openai_key) if openai_key else None
        fallback_filter = LLMMetadataFilter()
        return enhanced_filter, fallback_filter
    except Exception as e:
        st.error(f"❌ Failed to initialize LLM filters: {e}")
        return None, None

def get_collections(client):
    """Get list of available collections"""
    try:
        collections = client.collections.get_list()
        return collections.collection_names
    except Exception as e:
        st.error(f"❌ Failed to get collections: {e}")
        return []

def upload_document(client, collection_name, file, metadata=None):
    """Upload document to search collection"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Determine content type
        if file.name.lower().endswith('.csv'):
            content = {"type": "text", "text": file.getvalue().decode('utf-8')}
        elif file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            content = {"type": "image", "image": tmp_file_path}
        else:
            content = {"type": "text", "text": file.getvalue().decode('utf-8')}
        
        # Upload document
        result = client.documents.add(
            collection_name=collection_name,
            path=f"/tmp/{file.name}",
            content=content,
            metadata=metadata or {}
        )
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return result
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
        return None

def main():
    """Main application"""
    
    # Initialize clients
    client = initialize_search_client()
    enhanced_filter, fallback_filter = initialize_llm_filters()
    
    if not client:
        st.error("❌ Search client not available. Please check your configuration.")
        return
    
    # Sidebar - Left Menu
    with st.sidebar:
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2>Moment</h2>
            <p style="font-size: 0.9rem; color: #666;">Sports NLP Search</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Collection Management Section
        st.markdown("### 📚 Collections")
        
        # Create new collection
        new_collection = st.text_input("New Collection Name", placeholder="Enter collection name...")
        if st.button("➕ Create", use_container_width=True):
            if new_collection:
                try:
                    client.collections.add(new_collection)
                    st.success(f"✅ Created '{new_collection}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed: {e}")
        
        # Get existing collections
        collections = get_collections(client)
        selected_collection = st.selectbox("Select Collection", collections, placeholder="Choose a collection...") if collections else None
        
        # Collection Status (moved from main area)
        if selected_collection:
            st.markdown("---")
            st.markdown("### 📊 Collection Status")
            try:
                status = client.status.get_status()
                
                # Compact status display
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📄 Total", status.num_documents)
                    st.metric("✅ Indexed", status.num_indexed_documents)
                with col2:
                    st.metric("❌ Failed", status.num_failed_documents)
                    st.metric("⏳ Processing", status.num_parsing_documents + status.num_indexing_documents)
                    
            except Exception as e:
                st.error(f"❌ Status error: {e}")
        
        # Configuration Section
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        # Query mode selection
        query_mode = st.selectbox(
            "🔍 Query Mode",
            ["Enhanced AI (GPT-5 + Metadata)", "Basic LLM Filter"],
            help="Choose how to process your queries"
        )
        
        # Pagination settings
        st.markdown("**📄 Results per Page**")
        results_per_page = st.slider(
            "Results per Page",
            min_value=5,
            max_value=25,
            value=10,
            label_visibility="collapsed"
        )
        
        # Document Upload Section (collapsible)
        with st.expander("📤 Upload Documents", expanded=False):
            if selected_collection:
                uploaded_file = st.file_uploader(
                    "Choose a file",
                    type=['txt', 'pdf', 'csv', 'jpg', 'jpeg', 'png'],
                    help="Upload documents to add to your collection"
                )
                
                if uploaded_file:
                    # Metadata input
                    st.markdown("**📝 Document Metadata**")
                    doc_type = st.text_input("Document Type", value="document")
                    source = st.text_input("Source", value="uploaded")
                    tags = st.text_input("Tags (comma-separated)", value="")
                    priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
                    
                    if st.button("🚀 Upload", use_container_width=True):
                        with st.spinner("Uploading..."):
                            metadata = {
                                "type": doc_type,
                                "source": source,
                                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                                "priority": priority,
                                "upload_timestamp": time.time()
                            }
                            
                            result = upload_document(client, selected_collection, uploaded_file, metadata)
                            if result:
                                st.success("✅ Document uploaded successfully!")
                                st.json(result.document.__dict__)
            else:
                st.info("👈 Select a collection first to upload documents")
    
    # Main Content Area - Centered Chat Interface
    if selected_collection:
        # Welcome message
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>💬 Chat with {selected_collection}</h1>
            <p style="color: #666; font-size: 1.1rem;">Ask me anything about your sports data collection</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat Interface - Centered like ChatGPT
        chat_container = st.container()
        
        with chat_container:
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history in a centered container
            chat_messages = st.container()
            
            # Chat input at the bottom (centered)
            if prompt := st.chat_input("Ask me anything about your documents...", key="main_chat_input"):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display chat history
                with chat_messages:
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                
                # Generate response based on query mode
                with st.chat_message("assistant"):
                    with st.spinner("🤖 Processing your query..."):
                        try:
                            if query_mode == "Enhanced AI (GPT-5 + Metadata)" and enhanced_filter:
                                # Use high k value to get all results, then paginate in UI
                                result = enhanced_filter.execute_enhanced_query(
                                    selected_collection, prompt, k=100
                                )
                                response = result.get("response", "No response generated")
                                query_type = result.get("query_type", "unknown")
                                total_results = result.get("total_results", 0)
                                
                                # Display enhanced response header
                                st.markdown(f"**🔍 Query Type**: {query_type}")
                                st.markdown(f"**🤖 GPT-5 Interpretation**: {result.get('gpt_interpretation', {}).get('explanation', 'N/A')}")
                                st.markdown(f"**📊 Total Results**: {total_results}")
                                st.markdown("---")
                                
                                # Implement pagination for results
                                if total_results > 0:
                                    # Pagination controls
                                    total_pages = (total_results + results_per_page - 1) // results_per_page
                                    
                                    if total_pages > 1:
                                        col1, col2, col3 = st.columns([1, 2, 1])
                                        with col2:
                                            current_page = st.selectbox(
                                                f"Page (1-{total_pages})",
                                                range(1, total_pages + 1),
                                                key=f"page_{hash(prompt)}"
                                            )
                                        
                                        # Calculate start and end indices for current page
                                        start_idx = (current_page - 1) * results_per_page
                                        end_idx = min(start_idx + results_per_page, total_results)
                                        
                                        st.markdown(f"**📄 Showing results {start_idx + 1}-{end_idx} of {total_results}**")
                                    else:
                                        current_page = 1
                                        start_idx = 0
                                        end_idx = total_results
                                    
                                    # Display paginated results
                                    st.markdown(response)
                                    
                                    # Show pagination info at bottom
                                    if total_pages > 1:
                                        st.markdown(f"---")
                                        st.markdown(f"**📄 Page {current_page} of {total_pages}**")
                                else:
                                    st.markdown(response)
                                
                            elif query_mode == "Basic LLM Filter" and fallback_filter:
                                result = fallback_filter.execute_intelligent_query(
                                    selected_collection, prompt, k=100
                                )
                                response = result.get("response", "No response generated")
                                st.markdown(response)
                            
                            else:
                                # Fallback when neither mode is available
                                st.error("❌ Selected query mode is not available. Please check your configuration.")
                                response = "Query mode not available. Please check your configuration."
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                        except Exception as e:
                            error_msg = f"❌ Error processing query: {e}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Display chat history if no new input
            else:
                with chat_messages:
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
    
    else:
        # Welcome screen when no collection is selected
        st.markdown("""
        <div class="welcome-container">
            <h1> Welcome to Moment Sports NLP Search</h1>
            <p style="font-size: 1.2rem; margin: 2rem 0; opacity: 0.9;">
                Your intelligent companion for sports data analysis and insights
            </p>
            <div class="get-started-card">
                <h3>🚀 Get Started</h3>
                <p>1. Create a new collection in the sidebar</p>
                <p>2. Upload your sports documents</p>
                <p>3. Start chatting with your data!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show available collections
        if collections:
            st.markdown("### 📚 Available Collections")
            cols = st.columns(min(3, len(collections)))
            for i, collection in enumerate(collections):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="collection-card">
                        <h4>📁 {collection}</h4>
                        <p style="color: #666; font-size: 0.9rem;">Click to select</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("### 📚 No Collections Found")
            st.info("Create your first collection using the sidebar!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Moment - AI-Powered Sports Search & Analytics
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 