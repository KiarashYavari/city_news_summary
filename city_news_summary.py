import httpx
from fastapi import FastAPI, HTTPException
from typing import Dict
import asyncio

app = FastAPI()

def read_api_key(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read().strip()

NEWS_API_KEY = read_api_key('news_api_key.txt')
WEATHER_API_KEY = read_api_key('weather_api_key.txt')

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

async def fetch_weather(city: str) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{WEATHER_API_URL}?q={city}&appid={WEATHER_API_KEY}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Weather data not found")
        return response.json()

async def fetch_news(city: str) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NEWS_API_URL}?q={city}&apiKey={NEWS_API_KEY}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="News data not found")
        return response.json()

@app.get("/aggregator")
async def aggregator(city: str):
    weather_task = fetch_weather(city)
    news_task = fetch_news(city)

    # Run tasks concurrently
    weather_data, news_data = await asyncio.gather(weather_task, news_task)

    return {
        "city": city,
        "weather": weather_data,
        "news": news_data
    }
