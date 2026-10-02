from fastapi import APIRouter, HTTPException
from typing import List
import json
from googleapiclient.discovery import build
from duckduckgo_search import DDGS
from quizzly.core.config import settings
import os
from pydantic import BaseModel

router = APIRouter()

class TopicsRequest(BaseModel):
    topics: List[str]
    num_results: int = 5

@router.post("/articles")
async def get_articles(request: TopicsRequest):
    """
    Get articles based on provided topics using DuckDuckGo search
    """
    try:
        results = {}
        with DDGS() as ddgs:
            for topic in request.topics:
                search_results = ddgs.text(topic, max_results=request.num_results)
                articles = []
                for res in search_results:
                    title = res.get('title')
                    url = res.get('href')
                    if title and url:
                        articles.append({'title': title, 'url': url})
                results[topic] = articles
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube")
async def get_youtube_videos(request: TopicsRequest):
    """
    Get YouTube videos with thumbnails based on provided topics
    """
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API key not configured")
    
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        results = {}

        for topic in request.topics:
            search_response = youtube.search().list(
                q=topic,
                part='snippet',
                type='video',
                maxResults=request.num_results
            ).execute()

            youtube_data = []
            for item in search_response['items']:
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                video_id = item['id']['videoId']
                thumbnail_url = item['snippet']['thumbnails']['high']['url']
                youtube_data.append({
                    'title': video_title,
                    'video_url': video_url,
                    'thumbnail_url': thumbnail_url
                })
            
            results[topic] = youtube_data

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
