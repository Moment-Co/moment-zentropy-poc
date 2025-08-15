# Moment - Sports NLP Search

A comprehensive Streamlit application with **two distinct chat interfaces** for intelligent sports document search and analysis:

1. **🤖 GPT-5 Enhanced Search** - Sports-specific metadata filtering
2. **⚡ ZeroEntropy Native** - Full API functionality with search type selection

## 🎯 **Two Distinct Chat Interfaces**

### 1. 🤖 **GPT-5 Enhanced Search**

- **AI-powered sports metadata filtering**
- **Intelligent query interpretation** using GPT-5
- **Sports-specific filtering** for venues, teams, dates, players
- **Case-insensitive matching** for robust search results
- **Automatic filter generation** from natural language queries
- **Focused on sports games** with venue, team, and date recognition

### 2. ⚡ **ZeroEntropy Native**

- **Full API functionality** with all search types
- **Search Type Selection**:
  - 📄 **Top Documents** - Full document search with metadata
  - 📖 **Top Pages** - Page-level search with content
  - ✂️ **Top Coarse Snippets** - Broad snippet extraction
  - 🎯 **Top Fine Snippets** - Precise snippet extraction
- **Configurable parameters** (results per page, latency mode)
- **Direct API access** without LLM overhead
- **Complete control** over search parameters

## 🏗️ **Clean, Minimal Architecture**

```
zeroentropy-poc/
├── enhanced_streamlit_app.py    # Main UI with dual chat interfaces
├── zeroentropy_api.py          # Complete ZeroEntropy API client
├── quickstart.py               # Simple API testing script
├── launch.sh                   # One-click launcher
├── requirements.txt            # Minimal dependencies
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **Option 1: One-Click Launch**

```bash
./launch.sh
```

### **Option 2: Manual Setup**

1. **Clone and setup:**

   ```bash
   git clone <your-repo>
   cd zeroentropy-poc
   python -m venv zpoc
   source zpoc/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ZEROENTROPY_API_KEY=your_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Run the app:**
   ```bash
   streamlit run enhanced_streamlit_app.py
   ```

### **Option 3: Test API First**

```bash
python quickstart.py
```

## 🔑 **API Keys Required**

- **`ZEROENTROPY_API_KEY`**: Your ZeroEntropy API token
- **`OPENAI_API_KEY`**: Your OpenAI API key for GPT-5 features

## 📊 **Features**

### **Collection Management**

- Create, select, and manage collections
- Upload CSV and text documents
- View collection status and document counts
- **Automatic collection detection** from ZeroEntropy console

### **Dual Chat Interface**

- **Tab 1**: GPT-5 Enhanced Sports Search
- **Tab 2**: ZeroEntropy Native with full search options
- **Separate chat histories** for each mode
- **Independent configuration** for each interface

### **Smart Search Options**

- **GPT-5 Mode**: Natural language queries with AI interpretation
- **Native Mode**: Direct API search with type selection
- **Configurable pagination** and latency settings
- **Rich metadata display** for all result types

### **Sports-Specific Features**

- Venue/stadium name recognition
- Team name filtering
- Date-based searches
- Player name identification
- Case-insensitive matching

## 🎮 **Usage Examples**

### **GPT-5 Enhanced Search (Tab 1)**

```
"Show me all games at Etihad Stadium"
"Find matches where Manchester United played"
"Games from last season at Old Trafford"
"Liverpool vs Arsenal matches at Anfield"
```

### **ZeroEntropy Native (Tab 2)**

Choose your search type and query:

- **Documents**: "football match statistics"
- **Pages**: "game highlights page 5"
- **Coarse Snippets**: "team performance overview"
- **Fine Snippets**: "exact score details"

## 🔧 **API Endpoints Supported**

The `zeroentropy_api.py` client supports all ZeroEntropy API endpoints:

- **Collections**: Create, list, delete, status
- **Documents**: Add, update, delete, list, info
- **Search**: Documents, pages, snippets (coarse/fine)
- **Reranking**: Model-based document reranking

## 🚀 **Deployment**

### **Streamlit Cloud**

1. Push to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Set main file: `enhanced_streamlit_app.py`
4. Add API keys as secrets

### **Local Development**

```bash
./launch.sh
# or manually:
streamlit run enhanced_streamlit_app.py --server.port 8501
```

## 📝 **File Structure**

- **`enhanced_streamlit_app.py`**: Main application with dual chat interfaces
- **`zeroentropy_api.py`**: Complete ZeroEntropy API client wrapper
- **`quickstart.py`**: Simple API testing and demonstration
- **`launch.sh`**: One-click launcher with environment checks
- **`requirements.txt`**: Minimal dependencies for deployment
- **`.env`**: Environment variables (not in git)

## 🎯 **Benefits of Dual Interface**

✅ **Best of both worlds** - AI enhancement + full API access  
✅ **Sports-focused GPT-5** - Intelligent metadata filtering  
✅ **Complete ZeroEntropy exposure** - All search types available  
✅ **Independent chat histories** - Separate conversations per mode  
✅ **Flexible configuration** - Different settings per interface  
✅ **Professional UI** - Clean tabbed interface

## 🔍 **Interface Comparison**

| Feature                | GPT-5 Enhanced           | ZeroEntropy Native         |
| ---------------------- | ------------------------ | -------------------------- |
| **Focus**              | Sports games             | General documents          |
| **Intelligence**       | High (AI interpretation) | Basic (direct API)         |
| **Search Types**       | Documents only           | Documents, Pages, Snippets |
| **Metadata Filtering** | Automatic                | Manual                     |
| **Query Processing**   | Natural language         | Direct search              |
| **Use Case**           | Sports analysis          | General search             |

## 🆘 **Troubleshooting**

### **Common Issues**

- **API Key Errors**: Check `.env` file and Streamlit secrets
- **Import Errors**: Ensure all dependencies are installed
- **Search Failures**: Verify collection exists and documents are indexed
- **Collection Not Found**: Check ZeroEntropy console for existing collections

### **Support**

- Check ZeroEntropy API status at [api.zeroentropy.dev](https://api.zeroentropy.dev)
- Verify OpenAI API key validity
- Review Streamlit Cloud logs for deployment issues

---

**Moment - Sports NLP Search** | Powered by ZeroEntropy & OpenAI
