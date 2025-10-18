# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import shutil
from urllib.parse import quote
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import base64
# Import services and utilities
from services.openrouter_service import translate_text
from services.html_extract_service import extract_text_from_url
from services.qa_service import QAEngine
from utils.pdf_utils import extract_text_from_pdf, create_summary_pdf
from utils.text_chunker import chunk_text_simple
from utils.highlight import highlight_keywords
from utils.db_cache import get_url_cache, init_db, compute_source_key, get_cached_summary, save_to_cache, clear_old_cache, save_url_cache
from utils.logger import logger
from data.schemes import SCHEMES
from gtts import gTTS

# --- Configuration ---
load_dotenv()
SHARED_DIR = os.getenv("SHARED_DIR", "shared")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")

# --- Initialize Session State ---
def initialize_session_state():
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'summary_en' not in st.session_state:
        st.session_state.summary_en = ""
    if 'summary_te' not in st.session_state:
        st.session_state.summary_te = ""
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = ""
    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = QAEngine()
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = "Both"
    if 'keywords' not in st.session_state:
        st.session_state.keywords = ""
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All"
    if 'selected_scheme' not in st.session_state:
        st.session_state.selected_scheme = None
    # ADD THESE NEW LINES
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'source_type' not in st.session_state:
        st.session_state.source_type = ""

# --- Helper Functions ---
def generate_audio(text: str, lang: str = 'te') -> str | None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tts = gTTS(text=text, lang=lang)
            tts.save(tmp_audio.name)
            return tmp_audio.name
    except Exception as e:
        st.error(f"Could not generate audio: {e}")
        return None

def reset_session():
    """Resets the session state to start a new analysis."""
    st.session_state.processed = False
    st.session_state.summary_en = ""
    st.session_state.summary_te = ""
    st.session_state.pdf_path = ""
    st.session_state.qa_engine = QAEngine()
    st.session_state.keywords = ""
    st.session_state.selected_scheme = None
    # ADD THESE NEW LINES
    st.session_state.extracted_text = ""
    st.session_state.source_type = ""
    st.rerun()

def get_image_base64(img_path):
    """Convert image to base64 for embedding in HTML."""
    try:
        img = Image.open(img_path)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except:
        return ""

def get_schemes_by_category(category):
    """Get schemes filtered by category."""
    if category == "All":
        return SCHEMES
    return [scheme for scheme in SCHEMES if category == scheme.get("category", "Other")]

def get_schemes_by_tag(tag):
    """Get schemes filtered by tag."""
    return [scheme for scheme in SCHEMES if tag in scheme.get("tags", [])]

def get_categories():
    """Get all unique categories from schemes."""
    categories = set()
    for scheme in SCHEMES:
        categories.add(scheme.get("category", "Other"))
    return sorted(list(categories))

def create_scheme_distribution_chart():
    """Create a pie chart showing distribution of schemes by category."""
    categories = {}
    for scheme in SCHEMES:
        category = scheme.get("category", "Other")
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1
    
    fig = px.pie(
        values=list(categories.values()),
        names=list(categories.keys()),
        title="Distribution of Government Schemes by Category",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12),
        title_font=dict(family="Arial, sans-serif", size=16),
        height=500
    )
    return fig

def create_category_count_chart():
    """Create a bar chart showing count of schemes by category."""
    categories = {}
    for scheme in SCHEMES:
        category = scheme.get("category", "Other")
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1
    
    fig = px.bar(
        x=list(categories.keys()),
        y=list(categories.values()),
        title="Number of Schemes by Category",
        labels={"x": "Category", "y": "Number of Schemes"},
        color=list(categories.values()),
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12),
        title_font=dict(family="Arial, sans-serif", size=16),
        height=500
    )
    return fig

# --- Main Application ---
def main():
    # Initialize database and logger
    init_db()
    clear_old_cache(days_old=7) # Clean up old cache entries on startup
    initialize_session_state()

    # --- UI Layout ---
    st.set_page_config(page_title="AI-Sahayak", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #5E35B1;
            text-align: center;
            margin-bottom: 2rem;
        }
        .card {
            background-color: #F5F7FA;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .success-message {
            background-color: #E8F5E9;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #4CAF50;
        }
        .error-message {
            background-color: #FFEBEE;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #F44336;
        }
        .warning-message {
            background-color: #FFF8E1;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #FFC107;
        }
        .highlight {
            background-color: #FFF59D;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #757575;
            font-size: 0.8rem;
        }
        .language-selector {
            background-color: #E3F2FD;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .download-button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
            margin-right: 0.5rem;
        }
        .download-button:hover {
            background-color: #45a049;
        }
        .keyword-input {
            background-color: #F5F7FA;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .result-container {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 1rem;
        }
        .section-header {
            font-size: 1.5rem;
            color: #1E88E5;
            margin-bottom: 1rem;
            border-bottom: 2px solid #E3F2FD;
            padding-bottom: 0.5rem;
        }
        .share-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .share-button {
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
        }
        .whatsapp-button {
            background-color: #25D366;
        }
        .whatsapp-button:hover {
            background-color: #128C7E;
        }
        .copy-button {
            background-color: #6C757D;
        }
        .copy-button:hover {
            background-color: #5A6268;
        }
        .scheme-card {
            background-color: #FFFFFF;
            border-radius: 0.5rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .scheme-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .scheme-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1E88E5;
            margin-bottom: 0.5rem;
        }
        .scheme-category {
            display: inline-block;
            background-color: #E3F2FD;
            color: #1565C0;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
        .scheme-description {
            color: #424242;
            margin-bottom: 1rem;
        }
        .scheme-details {
            margin-top: 1rem;
        }
        .scheme-detail-title {
            font-weight: 600;
            color: #424242;
            margin-top: 0.5rem;
        }
        .scheme-detail-content {
            color: #616161;
            margin-bottom: 0.5rem;
        }
        .scheme-link {
            color: #1E88E5;
            text-decoration: none;
            font-weight: 500;
        }
        .scheme-link:hover {
            text-decoration: underline;
        }
        .category-tabs {
            display: flex;
            overflow-x: auto;
            margin-bottom: 1rem;
        }
        .category-tab {
            padding: 0.5rem 1rem;
            background-color: #F5F7FA;
            border: none;
            border-radius: 0.25rem;
            margin-right: 0.5rem;
            cursor: pointer;
            white-space: nowrap;
        }
        .category-tab.active {
            background-color: #1E88E5;
            color: white;
        }
        .user-type-selector {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .user-type-button {
            padding: 0.5rem 1rem;
            background-color: #F5F7FA;
            border: 1px solid #E0E0E0;
            border-radius: 0.25rem;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .user-type-button:hover {
            background-color: #E3F2FD;
        }
        .user-type-button.active {
            background-color: #1E88E5;
            color: white;
            border-color: #1E88E5;
        }
        .stats-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background-color: #FFFFFF;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            flex: 1;
            min-width: 200px;
            text-align: center;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1E88E5;
        }
        .stat-label {
            font-size: 0.9rem;
            color: #616161;
        }
        .hero-section {
            background: linear-gradient(135deg, #1E88E5, #5E35B1);
            color: white;
            padding: 2rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .hero-description {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        .hero-button {
            background-color: white;
            color: #1E88E5;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.25rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .hero-button:hover {
            background-color: #F5F7FA;
        }
        .qa-example {
            background-color: #F5F7FA;
            border: 1px solid #E0E0E0;
            border-radius: 0.25rem;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .qa-example:hover {
            background-color: #E3F2FD;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🇮🇳 AI-Sahayak: Government Scheme Explainer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Simplifying Indian government schemes for everyone.</p>', unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h2 class="hero-title">Discover Government Schemes Tailored for You</h2>
        <p class="hero-description">Find the right government schemes based on your profile and needs. Get detailed information in your preferred language.</p>
        <button class="hero-button">Explore Schemes</button>
    </div>
    """, unsafe_allow_html=True)

    # Statistics Section
    st.markdown('<h2 class="section-header">📊 Scheme Statistics</h2>', unsafe_allow_html=True)
    
    # Calculate statistics
    total_schemes = len(SCHEMES)
    categories = get_categories()
    total_categories = len(categories)
    
    # Count schemes by user type
    user_types = ["farmer", "student", "woman", "worker", "senior", "all"]
    user_type_counts = {}
    for user_type in user_types:
        user_type_counts[user_type] = len(get_schemes_by_tag(user_type))
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_schemes}</div>
            <div class="stat-label">Total Schemes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_categories}</div>
            <div class="stat-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{user_type_counts['farmer']}</div>
            <div class="stat-label">Farmer Schemes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{user_type_counts['student']}</div>
            <div class="stat-label">Student Schemes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_scheme_distribution_chart(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_category_count_chart(), use_container_width=True)

    # --- Sidebar for New Features ---
    with st.sidebar:
        st.header("🔧 Tools & Features")
        
        # Language Selection
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
        st.session_state.selected_language = st.selectbox(
            "Select Language Preference:",
            ["Both", "English", "Telugu"],
            index=0,
            key="language_selector"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # User Type Selection
        st.markdown('<h3 class="section-header">👤 Select Your Profile</h3>', unsafe_allow_html=True)
        user_type = st.selectbox(
            "I am a...",
            ["All", "Farmer", "Student", "Woman", "Senior Citizen", "Worker"],
            key="user_type_selector"
        )
        
        # Interactive Q&A
        if st.session_state.qa_engine.is_ready:
            with st.expander("🤔 Ask a Question about this Scheme"):
                # Add example questions
                st.markdown("**Example Questions:**")
                example_questions = [
                    "What is the eligibility criteria?",
                    "What are the benefits of this scheme?",
                    "How do I apply for this scheme?",
                    "What documents are required?",
                    "What is the last date to apply?"
                ]
                
                cols = st.columns(2)
                for i, q in enumerate(example_questions):
                    with cols[i % 2]:
                        if st.button(q, key=f"example_q_{i}"):
                            st.session_state.temp_question = q
                
                # Get question from session state or input
                if 'temp_question' in st.session_state:
                    user_question = st.text_input("Your question:", value=st.session_state.temp_question, key="user_question")
                    del st.session_state.temp_question
                else:
                    user_question = st.text_input("Your question:", key="user_question", placeholder="e.g., What is the last date to apply?")
                
                # Add advanced options
                with st.expander("⚙️ Advanced Options"):
                    show_context = st.checkbox("Show relevant context chunks", value=False)
                    use_full_text = st.checkbox("Search in full document (slower but more comprehensive)", value=False)
                
                if st.button("Ask", key="ask_button"):
                    if user_question:
                        with st.spinner("Thinking..."):
                            # Check if QA engine is ready
                            if not st.session_state.qa_engine.is_ready:
                                st.error("Q&A system is not ready. Please try generating the summary again.")
                            else:
                                # Get answer
                                answer_type, answer_text = st.session_state.qa_engine.ask(user_question)
                                
                                if answer_type == "Answer":
                                    st.success(answer_text)
                                    
                                    # Add feedback mechanism
                                    col1, col2, col3 = st.columns([1, 1, 2])
                                    with col1:
                                        if st.button("👍 Helpful", key="helpful"):
                                            st.session_state.feedback = "helpful"
                                            st.success("Thanks for your feedback!")
                                    with col2:
                                        if st.button("👎 Not Helpful", key="not_helpful"):
                                            st.session_state.feedback = "not_helpful"
                                            st.info("Thanks for your feedback. We'll work on improving our answers.")
                                    
                                    # Show context if requested
                                    if show_context:
                                        with st.expander("🔍 View Relevant Context"):
                                            snippets = st.session_state.qa_engine.get_relevant_snippets(user_question)
                                            if snippets:
                                                for i, snippet in enumerate(snippets):
                                                    st.markdown(f"**Context {i+1}:**")
                                                    st.markdown(snippet)
                                                    st.markdown("---")
                                            else:
                                                st.info("No relevant context found.")
                                    
                                    # Full text search option
                                    if use_full_text and "I couldn't find" in answer_text:
                                        with st.expander("🔍 Search in Full Document"):
                                            st.info("Searching in the full document for more information...")
                                            # Simple keyword search in full text
                                            keywords = user_question.lower().split()
                                            matches = []
                                            
                                            for chunk in st.session_state.qa_engine.text_chunks:
                                                chunk_lower = chunk.lower()
                                                score = sum(1 for keyword in keywords if keyword in chunk_lower)
                                                if score > 0:
                                                    matches.append((score, chunk))
                                            
                                            # Sort by relevance
                                            matches.sort(reverse=True)
                                            
                                            if matches:
                                                st.markdown("**Found these relevant sections:**")
                                                for score, match in matches[:3]:  # Show top 3
                                                    st.markdown(f"Relevance: {score}/{len(keywords)}")
                                                    st.markdown(match[:300] + "..." if len(match) > 300 else match)
                                                    st.markdown("---")
                                            else:
                                                st.info("No additional information found in the document.")
                                else:
                                    st.error(answer_text)
                                    
                                    # Offer help when answer isn't found
                                    if "couldn't find" in answer_text.lower():
                                        st.info("💡 **Tip:** Try rephrasing your question or use different keywords. You can also check the full summary above for more information.")
                    else:
                        st.warning("Please enter a question.")
        else:
            st.info("🤔 **Ask a Question** feature will be available after you generate a summary.")
            st.markdown("---")
        st.header("ℹ️ About")
        st.info("""
        AI-Sahayak simplifies Indian government schemes. 
        1. Provide a document via PDF, text, or URL.
        2. Click 'Generate Summary'.
        3. View the summary in English and Telugu.
        4. Download the PDF or ask questions about it.
        """)
        if st.button("Start New Analysis"):
            reset_session()

    # --- Main Content Area ---
    if not st.session_state.processed:
        # Tab Navigation
        tab1, tab2, tab3 = st.tabs(["📋 Browse Schemes", "📄 Document Analysis", "🔍 Scheme Search"])
        
        with tab1:
            # Category Tabs
            categories = ["All"] + get_categories()
            
            # Display category tabs
            category_tabs = st.tabs(categories)
            
            for i, category in enumerate(categories):
                with category_tabs[i]:
                    schemes = get_schemes_by_category(category)
                    
                    # Filter by user type if selected
                    if user_type != "All":
                        user_type_key = user_type.lower().replace(" ", "")
                        if user_type_key == "senior citizen":
                            user_type_key = "senior"
                        schemes = [s for s in schemes if user_type_key in s.get("tags", []) or "all" in s.get("tags", [])]
                    
                    # Display schemes
                    for scheme in schemes:
                        st.markdown(f"""
                        <div class="scheme-card">
                            <div class="scheme-title">{scheme['name']}</div>
                            <div class="scheme-category">{scheme.get('category', 'Other')}</div>
                            <div class="scheme-description">{scheme['description']}</div>
                            <div class="scheme-details">
                                <div class="scheme-detail-title">Benefits:</div>
                                <div class="scheme-detail-content">{scheme.get('benefits', 'N/A')}</div>
                                <div class="scheme-detail-title">Eligibility:</div>
                                <div class="scheme-detail-content">{scheme.get('eligibility', 'N/A')}</div>
                                <div class="scheme-detail-title">Application Process:</div>
                                <div class="scheme-detail-content">{scheme.get('application_process', 'N/A')}</div>
                                <a href="{scheme['url']}" target="_blank" class="scheme-link">Learn More</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab2:
            # Input Method Selection
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">📄 Input Method</h2>', unsafe_allow_html=True)
            input_method = st.selectbox("How would you like to provide the scheme details?", ("Upload PDF", "Paste Text", "Provide URL"))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Conditional Input Widgets
            if input_method == "Upload PDF":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
                if uploaded_file:
                    temp_extracted_text = extract_text_from_pdf(uploaded_file)
                    if not temp_extracted_text.startswith("Error:"):
                        st.session_state.extracted_text = temp_extracted_text
                        st.session_state.source_type = "pdf"
                    else:
                        st.markdown(f'<div class="error-message">{temp_extracted_text}</div>', unsafe_allow_html=True)
                        st.session_state.extracted_text = ""
                st.markdown('</div>', unsafe_allow_html=True)
            
            elif input_method == "Paste Text":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                text_input = st.text_area("Paste the scheme text here:", height=250)
                if text_input:
                    st.session_state.extracted_text = text_input
                    st.session_state.source_type = "text"
                st.markdown('</div>', unsafe_allow_html=True)
            
            elif input_method == "Provide URL":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                url_input = st.text_input("Enter the public URL of the scheme document:")
                if url_input:
                    with st.spinner("Fetching content..."):
                        # Check if we have cached content first
                        cached_content = get_url_cache(url_input)
                        if cached_content:
                            st.session_state.extracted_text = cached_content
                            st.info("📋 Using cached content from previous extraction (faster loading)")
                        else:
                            temp_extracted_text = extract_text_from_url(url_input)
                            if temp_extracted_text and not temp_extracted_text.startswith("Error:"):
                                # Cache the successful extraction for future use
                                save_url_cache(url_input, temp_extracted_text)
                                st.session_state.extracted_text = temp_extracted_text
                                st.success("✅ Content extracted and cached for future use")
                            else:
                                st.session_state.extracted_text = ""
                        
                        st.session_state.source_type = "url"
                        if st.session_state.extracted_text.startswith("Error:") or not st.session_state.extracted_text:
                            st.markdown(f'''
                            <div class="error-message">
                                {st.session_state.extracted_text if st.session_state.extracted_text else "No content could be extracted from the URL."}
                                <br><br>
                                <strong>💡 Suggestions:</strong>
                                <ol>
                                    <li>Copy the content directly from the website and paste it using the "Paste Text" option</li>
                                    <li>Download any available PDF documents and use the "Upload PDF" option</li>
                                    <li>Try a different URL if available (e.g., a specific scheme page instead of the homepage)</li>
                                    <li>Some government websites block automated access - manual copy-paste often works best</li>
                                </ol>
                            </div>
                            ''', unsafe_allow_html=True)
                            st.session_state.extracted_text = ""
                        else:
                            # Show preview of extracted text
                            st.markdown('<div class="success-message">Content extracted successfully!</div>', unsafe_allow_html=True)
                            with st.expander("Preview extracted content"):
                                st.text_area("Extracted text:", st.session_state.extracted_text[:1000] + "..." if len(st.session_state.extracted_text) > 1000 else st.session_state.extracted_text, height=200)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate Summary Section - This appears after any content is extracted
            if st.session_state.extracted_text and not st.session_state.processed:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-header">🚀 Generate Summary</h2>', unsafe_allow_html=True)
                
                # Keyword Input
                st.markdown('<div class="keyword-input">', unsafe_allow_html=True)
                st.markdown('<h3 class="section-header">🔑 Keywords (Optional)</h3>', unsafe_allow_html=True)
                keywords_input = st.text_input("Enter keywords to highlight (comma-separated):", placeholder="e.g., farmer, subsidy, eligibility")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Main Processing Button
                st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
                if st.button("🚀 Generate Summary", type="primary"):
                    if not st.session_state.extracted_text:
                        st.markdown('<div class="warning-message">Please provide scheme content using one of the methods above.</div>', unsafe_allow_html=True)
                    else:
                        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
                        st.session_state.keywords = keywords_input  # Store keywords in session state
                        source_key = compute_source_key(st.session_state.source_type, st.session_state.extracted_text[:10000])
                        
                        # Check Cache
                        cached_result = get_cached_summary(source_key)
                        if cached_result:
                            st.markdown('<div class="success-message">Found a cached summary!</div>', unsafe_allow_html=True)
                            st.session_state.summary_en = cached_result['summary_en']
                            st.session_state.summary_te = cached_result['summary_te']
                            st.session_state.pdf_path = cached_result['pdf_path']
                            st.session_state.processed = True
                            st.rerun()
                        else:
                            with st.spinner("AI is processing the document... This may take a moment."):
                                # 1. Summarize Chunks (First Pass)
                                chunks = chunk_text_simple(st.session_state.extracted_text)
                                chunk_summaries = []
                                progress_bar = st.progress(0, text="Starting summarization...")
                                for i, chunk in enumerate(chunks):
                                    progress_bar.progress((i + 1) / len(chunks), text=f"Summarizing chunk {i+1}/{len(chunks)}...")
                                    from services.openrouter_service import summarize_chunk
                                    summary = summarize_chunk(chunk)
                                    if not summary.startswith("Error:"):
                                        chunk_summaries.append(summary)
                                progress_bar.empty()
                                
                                if not chunk_summaries:
                                    st.markdown('<div class="error-message">Failed to summarize any part of the document.</div>', unsafe_allow_html=True)
                                    st.stop()
                                
                                # 2. Consolidate Summaries (Second Pass)
                                with st.spinner("Consolidating information..."):
                                    combined_summaries = "\n\n".join(chunk_summaries)
                                    final_chunks = chunk_text_simple(combined_summaries, max_chunk_size=4000)
                                    final_summaries = []
                                    from services.openrouter_service import get_openai_client
                                    client = get_openai_client()
                                    for chunk in final_chunks:
                                        consolidation_prompt = f"""
                                        You are an expert editor. Below are several summaries of a government scheme.
                                        Your task is to consolidate them into a single, clean, and non-redundant summary.
                                        The final summary must be in English and structured into exactly three categories with 3-4 bullet points each:
                                        1. Eligibility
                                        2. Benefits
                                        3. How to Apply
                                        Summaries to consolidate:
                                        ---
                                        {chunk}
                                        ---
                                        Final Consolidated Summary:
                                        """
                                        try:
                                            response = client.chat.completions.create(
                                                model=os.getenv("SUMMARIZATION_MODEL"),
                                                messages=[
                                                    {"role": "system", "content": "You are a helpful editor that consolidates repetitive summaries into a single, clean one."},
                                                    {"role": "user", "content": consolidation_prompt}
                                                ],
                                                temperature=0.2,
                                            )
                                            final_summaries.append(response.choices[0].message.content.strip())
                                        except Exception as e:
                                            logger.error(f"Error in final consolidation: {e}")
                                            final_summaries = chunk_summaries
                                            break
                                    st.session_state.summary_en = "\n\n".join(final_summaries)
                                
                                # 3. Translate
                                with st.spinner("Translating to Telugu..."):
                                    st.session_state.summary_te = translate_text(st.session_state.summary_en)
                                    if st.session_state.summary_te.startswith("Error:"):
                                        st.markdown('<div class="warning-message">AI translation failed. Using fallback translator.</div>', unsafe_allow_html=True)
                                        from deep_translator import GoogleTranslator
                                        try:
                                            st.session_state.summary_te = GoogleTranslator(source='en', target='te').translate(st.session_state.summary_en)
                                        except Exception as e:
                                            st.markdown(f'<div class="error-message">Fallback translation also failed: {e}</div>', unsafe_allow_html=True)
                                            st.session_state.summary_te = "Translation not available."
                                
                                # 4. Generate PDF
                                with st.spinner("Generating PDF..."):
                                    st.session_state.pdf_path = create_summary_pdf(st.session_state.summary_en, st.session_state.summary_te, SHARED_DIR)
                                    if not st.session_state.pdf_path:
                                        st.markdown('<div class="error-message">Failed to generate PDF.</div>', unsafe_allow_html=True)
                                        
                                        st.stop()
                                
                                # 5. Save to Cache & Prepare Q&A
                                save_to_cache(source_key, st.session_state.source_type, st.session_state.summary_en, st.session_state.summary_te, st.session_state.pdf_path)
                                
                                # Initialize Q&A engine with the full document
                                with st.spinner("Preparing Q&A system..."):
                                    qa_success = st.session_state.qa_engine.process_document(st.session_state.extracted_text)
                                    if not qa_success:
                                        st.warning("Q&A system could not be initialized. You can still view the summary.")
                                
                                st.session_state.processed = True
                                st.markdown('<div class="success-message">Summary generated successfully!</div>', unsafe_allow_html=True)
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            # Search functionality
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">🔍 Search Schemes</h2>', unsafe_allow_html=True)
            search_query = st.text_input("Search for schemes by name, category, or keywords:")
            
            if search_query:
                search_results = []
                search_query_lower = search_query.lower()
                
                for scheme in SCHEMES:
                    if (search_query_lower in scheme['name'].lower() or 
                        search_query_lower in scheme['description'].lower() or
                        search_query_lower in scheme.get('category', '').lower() or
                        any(search_query_lower in tag.lower() for tag in scheme.get('tags', []))):
                        search_results.append(scheme)
                
                if search_results:
                    st.markdown(f'<p>Found {len(search_results)} schemes matching "{search_query}":</p>', unsafe_allow_html=True)
                    
                    for scheme in search_results:
                        st.markdown(f"""
                        <div class="scheme-card">
                            <div class="scheme-title">{scheme['name']}</div>
                            <div class="scheme-category">{scheme.get('category', 'Other')}</div>
                            <div class="scheme-description">{scheme['description']}</div>
                            <div class="scheme-details">
                                <div class="scheme-detail-title">Benefits:</div>
                                <div class="scheme-detail-content">{scheme.get('benefits', 'N/A')}</div>
                                <div class="scheme-detail-title">Eligibility:</div>
                                <div class="scheme-detail-content">{scheme.get('eligibility', 'N/A')}</div>
                                <div class="scheme-detail-title">Application Process:</div>
                                <div class="scheme-detail-content">{scheme.get('application_process', 'N/A')}</div>
                                <a href="{scheme['url']}" target="_blank" class="scheme-link">Learn More</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p>No schemes found matching "{search_query}".</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Display Results ---
    if st.session_state.processed:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📄 Summary Results</h2>', unsafe_allow_html=True)
        
        # Get keywords from session state
        keywords = [k.strip() for k in st.session_state.get('keywords', '').split(',') if k.strip()]
        
        # Highlighting
        highlighted_en = highlight_keywords(st.session_state.summary_en, keywords)
        highlighted_te = highlight_keywords(st.session_state.summary_te, keywords)
        
        # Display based on language selection
        if st.session_state.selected_language == "Both":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<h3 class="section-header">English Summary</h3>', unsafe_allow_html=True)
                st.markdown(highlighted_en, unsafe_allow_html=True)
                st.markdown(get_download_button_html("Download as Text", st.session_state.summary_en, "summary_en.txt"), unsafe_allow_html=True)
            
            with col2:
                st.markdown('<h3 class="section-header">తెలుగు సారాంశం (Telugu Summary)</h3>', unsafe_allow_html=True)
                st.markdown(highlighted_te, unsafe_allow_html=True)
                st.markdown(get_download_button_html("టెక్స్ట్‌గా డౌన్‌లోడ్ చేయండి", st.session_state.summary_te, "summary_te.txt"), unsafe_allow_html=True)
        elif st.session_state.selected_language == "English":
            st.markdown('<h3 class="section-header">English Summary</h3>', unsafe_allow_html=True)
            st.markdown(highlighted_en, unsafe_allow_html=True)
            st.markdown(get_download_button_html("Download as Text", st.session_state.summary_en, "summary_en.txt"), unsafe_allow_html=True)
        else:  # Telugu
            st.markdown('<h3 class="section-header">తెలుగు సారాంశం (Telugu Summary)</h3>', unsafe_allow_html=True)
            st.markdown(highlighted_te, unsafe_allow_html=True)
            st.markdown(get_download_button_html("టెక్స్ట్‌గా డౌన్‌లోడ్ చేయండి", st.session_state.summary_te, "summary_te.txt"), unsafe_allow_html=True)
        
        # PDF Download
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            st.markdown('<h3 class="section-header">📥 Download Options</h3>', unsafe_allow_html=True)
            with open(st.session_state.pdf_path, "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="📥 Download Complete Summary PDF",
                data=pdf_data,
                file_name=os.path.basename(st.session_state.pdf_path),
                mime="application/pdf"
            )
            
            # Sharing - Fixed WhatsApp sharing
            st.markdown('<h3 class="section-header">📤 Share Summary</h3>', unsafe_allow_html=True)
            public_pdf_url = f"{BASE_URL}/{st.session_state.pdf_path}"
            
            # Create a properly formatted message
            summary_preview = st.session_state.summary_en[:200] + "..." if len(st.session_state.summary_en) > 200 else st.session_state.summary_en
            whatsapp_message = f"AI-Sahayak Scheme Summary:\n\n{summary_preview}\n\nFull PDF: {public_pdf_url}"
            
            # Properly URL encode the message
            encoded_message = quote(whatsapp_message)
            whatsapp_link = f"https://wa.me/?text={encoded_message}"
            
            # Display sharing options
            st.markdown('<div class="share-buttons">', unsafe_allow_html=True)
            st.markdown(f'<a href="{whatsapp_link}" target="_blank" class="share-button whatsapp-button">📤 Share on WhatsApp</a>', unsafe_allow_html=True)
            
            # Add copy link button
            if st.button("📋 Copy Link", key="copy_link"):
                # Use JavaScript to copy to clipboard
                st.components.v1.html(f"""
                <button onclick="navigator.clipboard.writeText('{public_pdf_url}')" 
                        style="background-color:#6C757D;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;">
                    📋 Link Copied!
                </button>
                <script>
                    document.querySelector('button').addEventListener('click', function() {{
                        this.textContent = '📋 Link Copied!';
                        setTimeout(() => {{
                            this.textContent = '📋 Copy Link';
                        }}, 2000);
                    }});
                </script>
                """, height=40)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display the public link
            st.markdown(f"**Public PDF Link:** {public_pdf_url}")
        
        # Optional Voice
        st.markdown('<h3 class="section-header">🔊 Audio Summary</h3>', unsafe_allow_html=True)
        if st.checkbox("🔊 Play Telugu Voice Summary"):
            if st.session_state.summary_te and not st.session_state.summary_te.startswith("Error:"):
                with st.spinner("Generating audio..."):
                    audio_path = generate_audio(st.session_state.summary_te)
                    if audio_path:
                        with open(audio_path, "rb") as audio_file:
                            audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        os.remove(audio_path)
            else:
                st.markdown('<div class="warning-message">No Telugu summary available to play.</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown('<div class="footer">© 2023 AI-Sahayak. All rights reserved.</div>', unsafe_allow_html=True)

def get_download_button_html(label, data, filename):
    """Generate HTML for a styled download button"""
    import base64
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-button">{label}</a>'
    return href



if __name__ == "__main__":
    main()