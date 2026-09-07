import streamlit as st
import requests

st.set_page_config(
    page_title="Northeast India Weather",
    page_icon="🌦️"
)

st.title("🌦️ Northeast India Weather Dashboard")

locations = {
    "Assam": (26.1445, 91.7362),
    "Arunachal Pradesh": (27.0844, 93.6053),
    "Manipur": (24.8170, 93.9368),
    "Meghalaya": (25.5788, 91.8933),
    "Mizoram": (23.7271, 92.7176),
    "Nagaland": (25.6751, 94.1086),
    "Sikkim": (27.3389, 88.6065),
    "Tripura": (23.9408, 91.9882)
}

state = st.selectbox(
    "Select a Northeast Indian state",
    list(locations.keys())
)

latitude, longitude = locations[state]

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ]
}

try:
    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        current = data["current"]

        st.subheader(f"Current Weather — {state}")

        st.metric(
            "Temperature",
            f"{current['temperature_2m']} °C"
        )

        st.write(
            "💧 Humidity:",
            f"{current['relative_humidity_2m']}%"
        )

        st.write(
            "🌧️ Precipitation:",
            f"{current['precipitation']} mm"
        )

        st.write(
            "💨 Wind Speed:",
            f"{current['wind_speed_10m']} km/h"
        )

    else:
        st.error("Unable to retrieve weather data.")

except Exception as e:
    st.error(f"Error connecting to weather service: {e}")
