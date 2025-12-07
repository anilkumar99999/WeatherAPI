from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

async def get_coordinates(city: str):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if not data or "results" not in data:
                logger.warning(f"No coordinates found for city: {city}")
                return None
            return data["results"][0]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in get_coordinates for city {city}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_coordinates for city {city}: {e}", exc_info=True)
        return None

async def get_weather(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in get_weather for {lat}, {lon}: {e}", exc_info=True)
        return {}
    except Exception as e:
        logger.error(f"Unexpected error in get_weather for {lat}, {lon}: {e}", exc_info=True)
        return {}

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message.strip()
    logger.info(f"Received message: {user_message}")

    # Simple heuristic: Assume the message IS the city name or contains it.
    # For a real chatbot, we'd use NLP. Here we just take the last word or the whole string.
    # Let's try to use the whole string first as a city search.
    
    city_name = user_message
    
    coords = await get_coordinates(city_name)
    
    if not coords:
        # Fallback: Try identifying a city in the message? 
        # For this simple demo, we'll just return a help message.
        return {
            "response": f"I couldn't find weather data for '{city_name}'. Please try entering just the city name (e.g., 'London', 'Tokyo')."
        }

    weather_data = await get_weather(coords["latitude"], coords["longitude"])
    
    if "current" not in weather_data:
        return {"response": "Sorry, I successfully found the city but couldn't retrieve the weather data."}
    
    temp = weather_data["current"]["temperature_2m"]
    unit = weather_data["current_units"]["temperature_2m"]
    
    return {
        "response": f"The current temperature in {coords['name']}, {coords.get('country', '')} is {temp}{unit}."
    }

@app.get("/")
def read_root():
    return {"message": "Weather Chatbot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
