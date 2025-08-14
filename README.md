# Moment - AI-Powered Sports Search

This project demonstrates advanced sports data search capabilities using Moment - Sports NLP Search, a state-of-the-art retrieval API for documents, pages, snippets and reranking, enhanced with LLM-powered natural language understanding.

## Setup

1. **Activate the virtual environment:**

   ```bash
   source zpoc/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key:**
   - Copy `env.example` to `.env`
   - Add your Moment - Sports NLP Search API key to the `.env` file
   ```bash
   cp env.example .env
   # Edit .env and add your actual API key
   ```

## Usage Examples

### ⚽ Streamlit Web Application (Recommended)

Launch the interactive web interface for managing sports data collections, uploading documents, and chatting with your corpus:

```bash
./launch_enhanced_streamlit.sh
```

Or manually:

```bash
source zpoc/bin/activate
streamlit run enhanced_streamlit_app.py
```

The Streamlit app provides:

- **Dashboard**: Overview of collections and documents
- **Collections Management**: Create, view, and delete collections
- **Document Upload**: Drag & drop interface for multiple file types
- **Chat Interface**: Natural language queries with real-time results
- **🧠 LLM-Enhanced Filtering**: Intelligent query analysis and metadata filtering

### Basic Example

Run the basic example to test your setup:

```bash
python basic_example.py
```

### Advanced Example

Run the advanced example with more features:

```bash
python advanced_example.py
```

### Async Example

Run the async example for better performance:

```bash
python async_example.py
```

### 🧠 LLM-Enhanced Filtering

Test the intelligent metadata filtering system:

```bash
python test_llm_filter.py
```

Or test the full system with your sports data:

```bash
python llm_metadata_filter.py
```

**Example Queries You Can Try:**

- "Show me all Manchester United games"
- "What games were played at Old Trafford?"
- "Find high scoring matches from August"
- "Liverpool vs Arsenal rivalry games"
- "Completed games this week"
- "Games with lots of goals"
- "Recent matches at Anfield"

## Project Structure

- `streamlit_app.py` - **Main Streamlit web application**
- `launch_streamlit.sh` - **Easy launcher script for the web app**
- `llm_metadata_filter.py` - **🧠 LLM-enhanced metadata filtering system**
- `test_llm_filter.py` - **Test script for LLM filtering features**
- `basic_example.py` - Simple Moment - Sports NLP Search usage example
- `advanced_example.py` - Advanced features demonstration
- `async_example.py` - Async/await pattern example
- `test_documents/` - Sample documents for testing
- `requirements.txt` - Python dependencies
- `env.example` - Environment configuration template

## Moment - Sports NLP Search Features

- **Collections Management**: Create, list, and delete collections
- **Document Processing**: Add, update, and delete documents
- **Search & Retrieval**: Query documents, pages, and snippets
- **Metadata Filtering**: Advanced filtering with JSON operators
- **Reranking**: Improve search results with reranking models
- **OCR Support**: Automatic PDF parsing and text extraction

## 🧠 LLM-Enhanced Features

- **Intelligent Query Analysis**: Natural language understanding and intent extraction
- **Smart Metadata Filtering**: Automatic filter generation from natural language queries
- **Pattern Recognition**: Team names, venues, dates, scores, and game status detection
- **Context-Aware Responses**: Rich, formatted responses with insights and suggestions
- **Advanced Filtering**: Complex boolean logic with $and, $or, $in, $nin operators
- **Sports-Specific Intelligence**: Built-in knowledge of Premier League teams, venues, and patterns

## API Limits

- Documents: Up to 2048 results
- Pages: Up to 1024 results
- Snippets: Up to 128 results
- Collections: Unlimited
- Metadata: Dict[str, str | list[str]]

## Error Handling

The examples include proper error handling for:

- `ConflictError`: When collections/documents already exist
- `HTTPStatusError`: For API communication issues
- Authentication errors: When API key is missing or invalid

## Getting Help

- [Moment - Sports NLP Search Documentation](https://docs.moment-sports-nlp.dev/)
- [API Reference](https://docs.moment-sports-nlp.dev/api-reference)
- [Community Support](https://docs.moment-sports-nlp.dev/support)
