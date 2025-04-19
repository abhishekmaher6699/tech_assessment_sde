import requests
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from datetime import datetime

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_table_if_not_exists():

    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            location VARCHAR(255),
            region VARCHAR(255),
            country VARCHAR(255),
            condition VARCHAR(255),
            temperature_c FLOAT,
            wind_speed_kph FLOAT,
            precipitation_mm FLOAT,
            date TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)

def save_to_db(data):
    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()

        check_query = """
        SELECT 1 FROM weather_data WHERE location = %s AND date = %s LIMIT 1;
        """
        cursor.execute(check_query, (data["location"], data["date"]))
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.close()
            connection.close()
            return {"message": "Record already exists in the database"}

        insert_query = sql.SQL(
            """
            INSERT INTO weather_data (location, region, country, condition, temperature_c, wind_speed_kph, precipitation_mm, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        )
        cursor.execute(
            insert_query,
            (
                data["location"],
                data["region"],
                data["country"],
                data["condition"],
                data["temperature_c"],
                data["wind_speed_kph"],
                data["precipitation_mm"],
                data["date"],
            ),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": "Record added successfully"}

    except Exception as e:
        print(e)



def read():

    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM weather_data;")
        rows = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        return [
            {
                "id": row[0],
                "location": row[1],
                "region": row[2],
                "country": row[3],
                "condition": row[4],
                "temperature_c": row[5],
                "wind_speed_kph": row[6],
                "precipitation_mm": row[7],
                "date": row[8],
            }
            for row in rows
        ]
    except Exception as e:
        print(e)


def delete(record_id):

    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM weather_data WHERE id = %s;", (record_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": f"Record with ID {record_id} deleted successfully."}
    except Exception as e:
        print(e)


def update(record_id, condition):
    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM weather_data WHERE id = %s;", (record_id,))
        existing_record = cursor.fetchone()

        if not existing_record:
            cursor.close()
            connection.close()
            return {"message": "Record not found"}
        
        cursor.execute( """
            UPDATE weather_data
            SET condition = %s
            WHERE id = %s;""", 
        (condition, record_id))
        connection.commit()

        cursor.close()
        connection.close()

        return {"message": "Condition updated successfully"}

    except Exception as e:
        print(e)

def download(format):
    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM weather_data;")
        records = cursor.fetchall()
        columns = ["id", "location", "region", "country", "condition", "temperature_c", "wind_speed_kph", "precipitation_mm", "date"]
        df = pd.DataFrame(records, columns=columns)
        df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (int, float)) else x)

        if format.lower() == "csv":
            file_path = "weather_data.csv"
            df.to_csv(file_path, index=False)
            cursor.close()
            connection.close()
            return FileResponse(file_path, media_type="text/csv", filename="weather_data.csv")

        elif format.lower() == "json":
            file_path = "weather_data.json"
            df.to_json(file_path, orient="records", indent=4)
            cursor.close()
            connection.close()
            return FileResponse(file_path, media_type="application/json", filename="weather_data.json")


        else:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'json'.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during data download: {e}")
