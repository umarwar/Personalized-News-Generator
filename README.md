

The **Personalized News Generator** is a Streamlit application designed to help users fetch news articles, ask questions about them, get summaries, and listen to audio versions of the content. It supports multiple languages and includes custom styling to enhance user experience.

## Features
- **Fetch News Articles:** Retrieve articles by entering a URL or title.
- **Ask Questions:** Submit questions related to the fetched article and get answers.
- **Summarize Articles:** Obtain concise summaries of the article.
- **Audio Playback:** Listen to both the article and the summary in audio format.
- **Multi-Language Support:** Translate content into English, Urdu, Spanish, and French.
- **Custom Styling:** Enhanced UI with custom CSS for improved readability.

## Technologies
- Streamlit
- FastAPI
- OpenAI API (LLaMA 3.1)
- Google Text-to-Speech (gTTS)

## FastAPI Backend

The backend is built using FastAPI and provides endpoints for fetching articles using url provided by the user, answering questions related to the article, summarizing content, and generating audio in famous languages.FastAPI is utilized to construct the backend for your Personalized News Generator application. It creates and manages endpoints that allow users to interact with the application’s core features. For instance, the /article endpoint enables users to fetch and process news articles either by URL or title. The backend then parses the article and handles tasks such as translating the content into different languages if needed.

### Endpoints

- **`/article`**: Fetches an article by URL or title. The article is downloaded, parsed, and stored in memory. Optionally, the article text can be translated into a specified language.
- **`/article_audio`**: Converts the fetched article text into audio format using Google Text-to-Speech (gTTS) and returns it as a streaming response.
- **`/summary_audio`**: Converts the generated summary into audio format using Google Text-to-Speech (gTTS) and returns it as a streaming response.
- **`/question`**: Accepts a question related to the fetched article and returns an AI-generated answer. The answer can be translated into a specified language.
- **`/summarize`**: Summarizes the fetched article text, with an option to limit the number of words. The summary can also be translated into a specified language.

### Key Components

- **Article Fetching**: Uses the `newspaper3k` library to download and parse articles from a given URL. If a title is provided, it searches for relevant articles using a news API.
- **Translation**: Utilizes the LLaMA 3.1 model for translating text into multiple languages, enhancing accessibility for non-English speakers.
- **Text-to-Speech**: Converts both article text and summaries into speech using Google Text-to-Speech (gTTS), allowing users to listen to the content.
- **In-Memory Storage**: Keeps the fetched article and summary in memory for quick access when generating audio or answering questions.


## Setting Up the Environment

### Creating a Virtual Environment

Before running the application, it's recommended to create a virtual environment to isolate dependencies and avoid conflicts with other projects.

1. **Install `virtualenv`** (if not already installed):
    ```bash
    pip install virtualenv
    ```

2. **Create a virtual environment**:
    ```bash
    virtualenv venv
    ```
    This will create a directory named `venv` in your project directory, containing the isolated Python environment.

3. **Activate the virtual environment**:
    - **On Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    - **On macOS and Linux**:
        ```bash
        source venv/bin/activate
        ```

    After activation, your terminal prompt should change to indicate that you are now working within the virtual environment.

4. **Deactivate the virtual environment** (when done):
    ```bash
    deactivate
    ```

### Running the Backend

To start the FastAPI backend:

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    ```

2. **Navigate to the project directory:**
    ```bash
    cd Personalized-News-Generator
    ```

3. **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```

### Running the Frontend

To run the Streamlit app:

1. **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

### Notes

- Ensure that the FastAPI backend is running locally at `http://127.0.0.1:8000` for the Streamlit app to work properly.
- Configure the API keys and endpoints according to your backend setup.
