from fastapi import FastAPI, HTTPException
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from backend.database import create_table_if_not_exists, save_to_db, delete, read, update, download

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

BASE_URL = "https://api.weatherapi.com/v1/current.json"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather API"}

@app.get("/get_weather/")
def get_weather(location: str):
    """
    Fetch weather data for a given location.
    """
    url = f"{BASE_URL}?key={API_KEY}&q={location}&aqi=no"

    try:
        response = requests.get(url) 
        response.raise_for_status()

        weather_data = response.json()

        if "error" in weather_data:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{location}' not found. Please provide a valid location."
            )

        filtered_data = {
            "location": weather_data["location"]["name"],
            "region": weather_data["location"]["region"],
            "country": weather_data["location"]["country"],
            "condition": weather_data["current"]["condition"]["text"],
            "temperature_c": weather_data["current"]["temp_c"],
            "wind_speed_kph": weather_data["current"]["wind_kph"],
            "precipitation_mm": weather_data["current"]["precip_mm"],
            "date": weather_data["location"]["localtime"],
        }

        save_to_db(filtered_data)

        return filtered_data

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=501,
            detail="An error occurred while fetching weather data. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/read_records/")
def read_records():
    """
    Fetch all records from the database.
    """
    try:
        records = read()
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/delete_record/")
def delete_record(record_id: int):
    """
    Delete a specific record by its ID.
    """
    try:
        delete(record_id)
        return {"message": "Record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/update_condition/{record_id}")
def update_record(record_id: int, condition: str):
    """
    Update the weather condition of a specific record by its ID.
    """
    try:
        result = update(record_id, condition)
        if "Record not found" in result:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_data/")
def download_data(format: str):
    """
    Download all records in the specified format (JSON or CSV).
    """
    try:
        return download(format)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
