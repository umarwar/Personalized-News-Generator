import streamlit as st
import requests

# Set page configuration
st.set_page_config(layout="wide")

API_URL = "https://your-fastapi-backend-url.com"

# Define language map
language_map = {"English": "en", "Urdu": "ur", "Spanish": "es", "French": "fr"}

# Apply custom CSS for styling
st.markdown("""
    <style>
    .title {
        text-align: center;
        color: brown;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .sidebar {
        background-color: #f5f5f5;
    }
    .content {
        text-align: justify; /* Justify text alignment */
    }
    .header {
        font-size: 2em;
        color: #0073e6;
    }
    .button-container {
        display: flex;
        gap: 10px; /* Space between buttons */
        margin-top: 5em; /* Space from the top */
    }
    </style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown('<div class="title">Personalized News Generator</div>', unsafe_allow_html=True)

# Sidebar for input fields and buttons
with st.sidebar:
    # Dropdown for input method
    option = st.selectbox("How do you want to enter the news?", ("URL", "Title"))

    # Language selection dropdown
    language = st.selectbox("Select the language for the article:", ("English", "Urdu", "Spanish", "French"))

    if option == "URL":
        url = st.text_input("Enter the news URL:")
        title = None
    else:
        title = st.text_input("Enter the news title:")
        url = None

    if st.button("Get Article", key="get_article", help="Fetch article based on URL or Title"):
        if url or title:
            response = requests.post(f"{API_URL}/article", json={"url": url, "title": title, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                data = response.json()
                st.session_state.article_text = data.get("article_text", "")
                st.session_state.authors = data.get("authors", [])
                st.session_state.source_url = data.get("source_url", "")
                st.session_state.summary = None
                st.session_state.answers = []  # Clear previous answers
            else:
                st.error(f"Failed to fetch article: {response.text}")
        else:
            st.error("Please enter a URL or title")

    question = st.text_input("Ask a question about the article:", key="question", label_visibility="collapsed", placeholder="Type your question here...")
    if st.button("Ask Question", key="ask_question", help="Ask a question about the fetched article"):
        if 'article_text' in st.session_state and question:
            response = requests.post(f"{API_URL}/question", json={"question": question, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.session_state.answers.append({"question": question, "answer": answer})
            else:
                st.error(f"Failed to get an answer for the question: {response.text}")
        else:
            st.error("Please enter a question or fetch an article first")
    
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    # Button with specific class for alignment
    if st.button("Summarize Article", key="summarize_article", help="Summarize the fetched article"):
        if 'article_text' in st.session_state:
            response = requests.post(f"{API_URL}/summarize", json={"max_words": 150, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                st.session_state.summary = response.json().get("summary", "Summary not available.")
            else:
                st.error(f"Failed to summarize the article: {response.text}")
        else:
            st.error("No article text available for summarization")
    st.markdown('</div>', unsafe_allow_html=True)

# Display Output (conditionally based on session state)
with st.container():
    if 'article_text' in st.session_state and st.session_state.article_text:
        # Highlight the source and authors at the top
        if st.session_state.authors:
            st.markdown(f"<p><strong>Author(s):</strong> <em>{', '.join(st.session_state.authors)}</em></p>", unsafe_allow_html=True)
        if st.session_state.source_url:
            st.markdown(f"<p><strong>Source:</strong> <a href='{st.session_state.source_url}' target='_blank'>Link to the article</a></p>", unsafe_allow_html=True)
        
        st.markdown('<div class="header">Article</div>', unsafe_allow_html=True)

        # Display the article text with justification
        st.markdown(f'<div class="content">{st.session_state.article_text}</div>', unsafe_allow_html=True)
        
        # Audio button for the article
        if st.button("🔊 Listen", key="listen_article"):
            response = requests.post(f"{API_URL}/article_audio")
            if response.status_code == 200:
                audio_data = response.content
                st.audio(audio_data, format="audio/mp3")
            else:
                st.error(f"Failed to retrieve the article audio: {response.text}")

    if 'summary' in st.session_state and st.session_state.summary:
        st.markdown('<div class="header">Summary</div>', unsafe_allow_html=True)
        # Display the summary with justification
        st.markdown(f'<div class="content">{st.session_state.summary}</div>', unsafe_allow_html=True)

        # Audio button for the summary
        if st.button("🔊 Listen", key="listen_summary"):
            response = requests.post(f"{API_URL}/summary_audio")
            if response.status_code == 200:
                audio_data = response.content
                st.audio(audio_data, format="audio/mp3")
            else:
                st.error(f"Failed to retrieve the summary audio: {response.text}")

    if 'answers' in st.session_state and st.session_state.answers:
        st.markdown('<div class="header">Q&A</div>', unsafe_allow_html=True)
        for qa in st.session_state.answers:
            st.markdown(f"**Q: {qa['question']}**")
            st.markdown(f"A: {qa['answer']}")
