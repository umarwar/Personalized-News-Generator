from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from newspaper import Article
import openai
import aiohttp
import asyncio
from gtts import gTTS
from io import BytesIO
from starlette.responses import StreamingResponse

app = FastAPI()

api_key = "2447d931642844d38c63f5918e032ac6"
base_url = "https://api.aimlapi.com"

openai.api_key = api_key
openai.api_base = base_url

article_storage = {}

class ArticleRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = "en"

class QuestionRequest(BaseModel):
    question: str
    language: str  # Include language for question answers

class SummaryRequest(BaseModel):
    max_words: int = 200
    language: str  # Include language for summary

async def fetch_article_text(url):
    loop = asyncio.get_event_loop()
    try:
        article = Article(url)
        await loop.run_in_executor(None, article.download)
        await loop.run_in_executor(None, article.parse)
        return article.text, article.authors, article.source_url
    except Exception as e:
        print(f"Error fetching article: {e}")
        raise HTTPException(status_code=400, detail="Failed to fetch article")

async def translate_text(text, target_language):
    try:
        response = await openai.ChatCompletion.acreate(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        translated_text = response.choices[0].message['content']
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail="Error translating text")

        # # "AIzaSyBXcCdHXzgqCkEk_QufV62-0fVTfsFK7dI"
        # YOUR_GOOGLE_API_KEY = "AIzaSyAUw7wqL8-2x9UCp_qAEOvtDZCvAjbCW0U"
        # YOUR_CUSTOM_SEARCH_ENGINE_ID = "8380278bfbbb94fd5"

async def fetch_article_by_title(title):
    api_key = "AIzaSyAUw7wqL8-2x9UCp_qAEOvtDZCvAjbCW0U"
    search_engine_id = "8380278bfbbb94fd5"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={requests.utils.quote(title)}&key={api_key}&cx={search_engine_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status()
                search_results = await response.json()

                # # Debugging
                # print("Search Results:", search_results)

                if 'items' not in search_results or not search_results['items']:
                    print("No articles found for the given title.")
                    return None, None, None
                
                first_result = search_results['items'][0]
                article_url = first_result.get("link")
                
                # # Debugging
                # print("First Article URL:", article_url)

                article_text, authors, source_url = await fetch_article_text(article_url)
                return article_text, authors, source_url
    
    except aiohttp.ClientError as e:
        print(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail="Error fetching articles from the search API")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


def generate_audio(text: str, language: str) -> StreamingResponse:
    try:
        tts = gTTS(text=text, lang=language)
        audio_stream = BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail="Error generating audio")

@app.post("/article")
async def analyze_article(request: ArticleRequest):
    if not request.url and not request.title:
        raise HTTPException(status_code=400, detail="URL or title must be provided")

    if request.url:
        article_text, authors, source_url = await fetch_article_text(request.url)
    else:
        article_text, authors, source_url = await fetch_article_by_title(request.title)

    # Translate the article text to the specified language
    if request.language != "en":
        article_text = await translate_text(article_text, request.language)

    article_storage['text'] = article_text

    return {
        "article_text": article_text,
        "authors": authors,
        "source_url": source_url
    }

@app.post("/article_audio")
async def article_audio():
    if 'text' not in article_storage:
        raise HTTPException(status_code=400, detail="No article text available for audio generation")

    article_text = article_storage['text']
    language = "en"  # Change to match the stored language

    return generate_audio(article_text, language)

@app.post("/summary_audio")
async def summary_audio():
    if 'summary' not in article_storage:
        raise HTTPException(status_code=400, detail="No summary available for audio generation")

    summary_text = article_storage['summary']
    language = "en"  # Change to match the stored language if necessary

    return generate_audio(summary_text, language)

@app.post("/question")
async def ask_question(request: QuestionRequest):
    if 'text' not in article_storage:
        raise HTTPException(status_code=400, detail="No article text available for questioning")

    article_text = article_storage['text']
    
    messages = [
        {"role": "system", "content": "You are an AI assistant who knows everything."},
        {"role": "user", "content": article_text},
        {"role": "user", "content": f"Question: {request.question}"}
    ]

    try:
        response = await openai.ChatCompletion.acreate(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        answer = response.choices[0].message['content']
        
        # Translate the answer to the specified language
        if request.language != "en":
            answer = await translate_text(answer, request.language)

    except Exception as e:
        print(f"Error processing the question with Lemma API: {e}")
        raise HTTPException(status_code=500, detail="Error processing the question with Lemma API")

    return {"answer": answer}

@app.post("/summarize")
async def summarize(request: SummaryRequest):
    if 'text' not in article_storage:
        raise HTTPException(status_code=400, detail="No article text available for summarization")

    text = article_storage['text']
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Summarize the following article in a concise manner:"},
                {"role": "user", "content": text},
            ],
            temperature=0.7,
            max_tokens=512,
        )
        summary = response.choices[0].message['content']
        
        # Translate the summary to the specified language
        if request.language != "en":
            summary = await translate_text(summary, request.language)
        
        # Store the summary in article_storage
        article_storage['summary'] = summary

    except Exception as e:
        print(f"Error summarizing the article with Lemma API: {e}")
        raise HTTPException(status_code=500, detail="Error summarizing the article with Lemma API")

    return {"summary": summary}


# url = "https://www.dawn.com/news/1852663/remarkable-achievement-coas-munir-lauds-arshad-nadeem-for-olympic-win"
# text, author, surl = fetch_article_text(url)
# # print(surl)
# title  = "Some India doctors stay off job after strike over colleague’s rape and murder"
# text, author, surl = fetch_article_by_title(title)
# print(text)
# import asyncio

# async def main():
#     audio_url = await generate_audio("hello my name is Umar", "en")
#     print(audio_url)

# asyncio.run(main())