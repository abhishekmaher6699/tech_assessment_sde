import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Weather & Location Dashboard",
    page_icon="🌤️",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"  
YOUTUBE_API_KEY = os.getenv("YT_API_KEY")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_youtube_videos(query):
    try:
        params = {
            "part": "snippet",
            "q": query + ' weather',
            "type": "video",
            "key": YOUTUBE_API_KEY,
            "maxResults": 5,
        }
        response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching YouTube videos: {e}")
        return []

def get_weather_emoji(condition):
    condition = condition.lower() if condition else ""
    if "clear" in condition or "sunny" in condition:
        return "☀️"
    elif "cloud" in condition:
        return "☁️"
    elif "rain" in condition:
        return "🌧️"
    elif "snow" in condition:
        return "❄️"
    elif "thunder" in condition or "storm" in condition:
        return "⛈️"
    elif "fog" in condition or "mist" in condition:
        return "🌫️"
    else:
        return "🌤️"


with st.sidebar:
    st.title("🌤️ Weather Dashboard")
    st.markdown("---")
    section = st.radio("Navigation", ["Current Weather", "Search History"])

    st.markdown("---")
    st.markdown("### Assessment Additional Information")
    st.markdown("""
    **Name: Abhishek Maher**
      
    **PM Accelerator Program**  
    The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.
    """)

if section == "Current Weather":
    st.title("Current Weather")

    col1, col2 = st.columns([3, 1])

    with col1:
        location = st.text_input("Enter City or Location", placeholder="e.g., New York, London, Tokyo")

    with col2:
        st.write(" ")
        st.write(" ")
        search_button = st.button("Get Weather 🔍", use_container_width=True)

    if search_button and location:
        try:
            with st.spinner(f"Fetching weather data for {location}..."):
                response = requests.get(f"{API_URL}/get_weather/", params={"location": location}, timeout=10)
                response.raise_for_status()
                weather_data = response.json()

                col1, col2 = st.columns([2, 1])

                with col1:
                    location_name = weather_data.get('location', location)
                    region = weather_data.get('region', '')
                    country = weather_data.get('country', '')
                    location_display = f"{location_name}"
                    if region and country:
                        location_display += f", {region}, {country}"
                    elif country:
                        location_display += f", {country}"

                    st.markdown(f"### Weather in {location_display}")

                    condition = weather_data.get('condition', 'N/A')
                    emoji = get_weather_emoji(condition)
                    st.markdown(f"#### {condition} {emoji}")

                    metric_cols = st.columns(3)
                    with metric_cols[0]:
                        st.metric("Temperature", f"{weather_data.get('temperature_c', 'N/A')}°C")
                    with metric_cols[1]:
                        st.metric("Precipitation", f"{weather_data.get('precipitation_mm', 'N/A')} mm")
                    with metric_cols[2]:
                        st.metric("Wind Speed", f"{weather_data.get('wind_speed_kph', 'N/A')} km/h")

            with st.spinner(f"Searching YouTube videos about {location}..."):
                videos = fetch_youtube_videos(location)
                if videos:
                    st.markdown("### Related YouTube Videos")
                    video_columns = st.columns(2) 

                    for idx, video in enumerate(videos[:4]): 
                        title = video["snippet"]["title"]
                        video_id = video["id"]["videoId"]
                        thumbnail_url = video["snippet"]["thumbnails"]["medium"]["url"]

                        with video_columns[idx % 2]: 
                            st.markdown(
                                f"""
                                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" style="text-decoration: none;">
                                    <img src="{thumbnail_url}" alt="{title}" style="width: 100%; max-width: 320px; border-radius: 10px;"/>
                                    <p style="margin-top: 5px; font-size: 16px; color: white; ">{title}</p>
                                </a>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.info("No videos found for this location.")

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again later.")
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to the weather service. Please check your internet connection or try again later.")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                st.error("Location not found. Please check the location name and try again.")
            elif status_code == 503:
                st.error("The weather service is currently unavailable. Please try again later.")
            else:
                st.error(f"An error occurred: {e}")
        except ValueError:
            st.error("Received unexpected data from the server.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

elif section == "Search History":
    st.title("Search History")

    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("Previous Weather Searches")

    try:
        with st.spinner("Loading search history..."):
            response = requests.get(f"{API_URL}/read_records/", timeout=10)
            response.raise_for_status()
            records = response.json()

            if records:
                df = pd.DataFrame(records)

                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.markdown("---")
                st.markdown("### Manage Records")
                col1, col2, col3, col4 = st.columns([3, 2, 2, 3])

                with col1:
                    action = st.radio("Action:", ["Edit", "Delete"], horizontal=True, label_visibility="collapsed")

                with col2:
                    if not df.empty:
                        selected_record = st.selectbox(
                            "Select Record:",
                            options=df['id'].tolist(),
                            format_func=lambda x: f"#{x} - {df[df['id'] == x]['location'].values[0]}"
                        )

                with col4:
                    if action == "Delete" and selected_record:
                        if st.button("Delete", key="delete_button", use_container_width=True):
                            try:
                                delete_response = requests.get(f"{API_URL}/delete_record/", params={"record_id": selected_record}, timeout=10)
                                delete_response.raise_for_status()
                                st.success(f"Record #{selected_record} deleted.")
                                st.rerun()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Error deleting record: {e}")

                    elif action == "Edit" and selected_record:
                        selected_row = df[df['id'] == selected_record]
                        current_condition = selected_row['condition'].values[0] if len(selected_row) > 0 else ""
                        new_condition = st.text_input("New Condition:", value=current_condition, key="condition_input")

                        if st.button("Update", key="update_button", use_container_width=True):
                            try:
                                update_response = requests.put(
                                    f"{API_URL}/update_condition/{selected_record}",
                                    params={"condition": new_condition},
                                    timeout=10
                                )
                                update_response.raise_for_status()
                                st.success(f"Record updated.")
                                st.rerun()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Error updating record: {e}")

                st.markdown("---")
                st.markdown("### Export Data")

                col1, col3 = st.columns([6, 3])

                with col1:
                    st.write("Export your search history data in different formats.")

                with col3:
                    export_format = st.selectbox("Format:", ["JSON", "CSV"], label_visibility="collapsed")                
                    if st.button("Export", key="export_btn", use_container_width=True):
                        try:
                            format_param = export_format.lower()
                            download_url = f"{API_URL}/download_data/?format={format_param}"
                            st.markdown(f"""
                                <a href="{download_url}" target="_blank">
                                    <button>Download {export_format}</button>
                                </a>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error exporting data: {e}")
            else:
                st.info("No search history found.")
    except requests.exceptions.Timeout:
        st.error("The request timed out while loading search history. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the server. Please check your internet connection.")
    except ValueError:
        st.error("Received unexpected data from the server.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
