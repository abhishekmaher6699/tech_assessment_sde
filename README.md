# Weather App Backend (Tech Assessment 2)

This repository contains a backend implementation for a weather app, built using **FastAPI**. The app supports CRUD operations with a PostgreSQL database, integrates third-party APIs, and provides weather information along with location-specific YouTube videos. A simple **Streamlit** frontend is also included for user interaction.

---

## Features

### 1. Weather Information Retrieval
- Users can input a location name to get the current weather.
- Data is fetched from the free [WeatherAPI](https://www.weatherapi.com/).
- Key weather details such as temperature, wind speed, and precipitation are shown.

### 2. CRUD Operations with PostgreSQL
- **CREATE**: Users can store location-specific weather data into the database.
- **READ**: Users can retrieve previously stored weather records.
- **UPDATE**: Users can update specific field (e.g., weather condition text) in the database.
- **DELETE**: Users can delete specific records.

### 3. Data Export
- Supports exporting data from the database in **JSON** or **CSV** format.

### 4. API Integration
- Integrates YouTube API to fetch location-specific videos.

---

## How to Run the Project

### Prerequisites
1. Set up a PostgreSQL database.
2. Obtain API keys for:
   - [WeatherAPI](https://www.weatherapi.com/)
   - [YouTube API](https://developers.google.com/youtube/v3)

### Setup Instructions

#### 1. Clone the Repository
```bash
$ git clone https://github.com/abhishekmaher6699/tech_assessment_sde.git
```

#### 2. Create a `.env` File
In the root directory, create a `.env` file with the following content:

```env
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

WEATHER_API_KEY = "your_weather_api_key"
YT_API_KEY = "your_youtube_api_key"
```

#### 3. Install Dependencies
Use `pip` to install the required Python libraries:

```bash
$ pip install -r requirements.txt
```


#### 4. Run the Backend Server
Start the FastAPI backend server:

```bash
$ uvicorn backend.app:app --reload
```

#### 5. Run the Frontend
Navigate to the `frontend` directory and run the Streamlit app:

```bash
$ streamlit run frontend/app.py
```

---
## Tech Stack

FastAPI

Streamlit

PostgreSQL

WeatherAPI

YouTube API

---

## API Endpoints

### 1. Weather Data Retrieval
**Endpoint:** `GET /get_weather/`

**Query Parameter:**
- `location` (str): The location to fetch weather data for.

**Example Request:**
```bash
$ curl -X GET "http://localhost:8000/get_weather/?location=London"
```

### 2. CRUD Operations
- **Read Records:** `GET /read_records/`
- **Delete Record:** `GET /delete_record/` (Requires `record_id` as query parameter.)
- **Update Condition:** `PUT /update_condition/{record_id}`

### 3. Data Export
**Endpoint:** `GET /download_data/`

**Query Parameter:**
- `format` (str): The format to download data in (`json` or `csv`).

---

Feel free to reach out for any queries or issues!

