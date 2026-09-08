import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from streamlit_autorefresh import st_autorefresh
from io import BytesIO


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Northeast India Disaster Management",
    page_icon="🚨",
    layout="wide"
)


# =========================================================
# AUTOMATIC REFRESH
# Refresh every 5 minutes
# =========================================================

st_autorefresh(
    interval=5 * 60 * 1000,
    key="weather_refresh"
)


# =========================================================
# TITLE
# =========================================================

st.title("🚨 Northeast India Disaster Management")

st.subheader(
    "🌦️ Weather Monitoring & Multilingual Early Warning System"
)

st.info(
    "Monitor weather conditions, assess disaster risk and receive "
    "multilingual warning messages for the Northeast Indian states."
)


# =========================================================
# NORTHEAST INDIA LOCATIONS
# =========================================================

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


# =========================================================
# LANGUAGES
# =========================================================

languages = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Tamil": "ta",
    "Urdu": "ur",
    "Punjabi": "pa"
}


# =========================================================
# WEATHER DESCRIPTION
# =========================================================

def weather_description(code):

    code = int(code)

    weather_codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Depositing rime fog",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        56: "🌧️ Light freezing drizzle",
        57: "🌧️ Dense freezing drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        66: "🌧️ Light freezing rain",
        67: "🌧️ Heavy freezing rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "❄️ Heavy snow",
        77: "🌨️ Snow grains",
        80: "🌦️ Slight rain showers",
        81: "🌧️ Moderate rain showers",
        82: "⛈️ Violent rain showers",
        85: "🌨️ Slight snow showers",
        86: "🌨️ Heavy snow showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with hail",
        99: "⛈️ Severe thunderstorm with hail"
    }

    return weather_codes.get(code, "🌥️ Unknown weather")


# =========================================================
# RISK CALCULATION
# =========================================================

def calculate_risk(
    precipitation,
    wind_speed,
    humidity,
    temperature
):

    score = 0

    # Rainfall
    if precipitation >= 50:
        score += 3
    elif precipitation >= 20:
        score += 2
    elif precipitation >= 10:
        score += 1

    # Wind speed
    if wind_speed >= 60:
        score += 3
    elif wind_speed >= 40:
        score += 2
    elif wind_speed >= 25:
        score += 1

    # Humidity
    if humidity >= 90:
        score += 1

    # Temperature
    if temperature >= 40:
        score += 2

    # Risk level
    if score >= 6:
        risk = "HIGH"
    elif score >= 3:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return risk, score


# =========================================================
# WARNING MESSAGE
# =========================================================

def generate_warning(state, risk, precipitation, wind_speed):

    if risk == "HIGH":
        warning = (
            f"High risk alert for {state}. "
            "Heavy or hazardous weather conditions may be present. "
            "Please take necessary safety measures and follow "
            "official disaster warnings."
        )

    elif risk == "MEDIUM":
        warning = (
            f"Medium risk alert for {state}. "
            "Weather conditions require caution. "
            "Please monitor weather updates and follow official advice."
        )

    else:
        warning = (
            f"Low risk conditions detected for {state}. "
            "Continue monitoring weather updates and remain prepared."
        )

    if precipitation >= 20:
        warning += (
            " Heavy rainfall may increase the possibility of "
            "flooding or landslide-related hazards."
        )

    if wind_speed >= 40:
        warning += (
            " Strong winds may create hazardous conditions."
        )

    return warning


# =========================================================
# MULTILINGUAL WARNING TEXT
# =========================================================

def translate_warning(state, risk, language):

    warnings = {

        "English": {
            "HIGH":
                f"High risk alert for {state}. Please take necessary "
                "safety measures and follow official disaster warnings.",
            "MEDIUM":
                f"Medium risk alert for {state}. Please remain cautious "
                "and monitor official weather updates.",
            "LOW":
                f"Low risk conditions detected for {state}. "
                "Continue monitoring weather updates."
        },

        "Hindi": {
            "HIGH":
                f"{state} के लिए उच्च जोखिम चेतावनी। कृपया आवश्यक "
                "सुरक्षा उपाय करें और आधिकारिक आपदा चेतावनियों का पालन करें।",
            "MEDIUM":
                f"{state} के लिए मध्यम जोखिम चेतावनी। कृपया सावधान रहें "
                "और आधिकारिक मौसम जानकारी पर नजर रखें।",
            "LOW":
                f"{state} में कम जोखिम की स्थिति है। "
                "मौसम की जानकारी पर नजर रखें।"
        },

        "Telugu": {
            "HIGH":
                f"{state} కు అధిక ప్రమాద హెచ్చరిక. దయచేసి అవసరమైన "
                "భద్రతా చర్యలు తీసుకుని అధికారిక విపత్తు హెచ్చరికలను పాటించండి.",
            "MEDIUM":
                f"{state} కు మధ్యస్థ ప్రమాద హెచ్చరిక. దయచేసి జాగ్రత్తగా "
                "ఉండి అధికారిక వాతావరణ సమాచారాన్ని గమనించండి.",
            "LOW":
                f"{state} లో తక్కువ ప్రమాద పరిస్థితులు ఉన్నాయి. "
                "వాతావరణ సమాచారాన్ని గమనిస్తూ ఉండండి."
        },

        "Bengali": {
            "HIGH":
                f"{state} এর জন্য উচ্চ ঝুঁকির সতর্কতা। অনুগ্রহ করে "
                "প্রয়োজনীয় নিরাপত্তা ব্যবস্থা নিন এবং সরকারি সতর্কতা অনুসরণ করুন।",
            "MEDIUM":
                f"{state} এর জন্য মাঝারি ঝুঁকির সতর্কতা। সতর্ক থাকুন "
                "এবং সরকারি আবহাওয়ার তথ্য পর্যবেক্ষণ করুন।",
            "LOW":
                f"{state} এ কম ঝুঁকির পরিস্থিতি রয়েছে। "
                "আবহাওয়ার তথ্য পর্যবেক্ষণ করুন।"
        },

        "Gujarati": {
            "HIGH":
                f"{state} માટે ઉચ્ચ જોખમની ચેતવણી. કૃપા કરીને જરૂરી "
                "સુરક્ષા પગલાં લો અને સત્તાવાર ચેતવણીઓનું પાલન કરો.",
            "MEDIUM":
                f"{state} માટે મધ્યમ જોખમની ચેતવણી. સાવચેત રહો "
                "અને સત્તાવાર હવામાન માહિતી તપાસતા રહો.",
            "LOW":
                f"{state} માં ઓછા જોખમની સ્થિતિ છે. "
                "હવામાનની માહિતી પર નજર રાખો."
        },

        "Kannada": {
            "HIGH":
                f"{state} ಗೆ ಹೆಚ್ಚಿನ ಅಪಾಯದ ಎಚ್ಚರಿಕೆ. ದಯವಿಟ್ಟು ಅಗತ್ಯ "
                "ಸುರಕ್ಷತಾ ಕ್ರಮಗಳನ್ನು ಕೈಗೊಂಡು ಅಧಿಕೃತ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಪಾಲಿಸಿ.",
            "MEDIUM":
                f"{state} ಗೆ ಮಧ್ಯಮ ಅಪಾಯದ ಎಚ್ಚರಿಕೆ. ಎಚ್ಚರಿಕೆಯಿಂದಿರಿ "
                "ಮತ್ತು ಅಧಿಕೃತ ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ಗಮನಿಸಿ.",
            "LOW":
                f"{state} ನಲ್ಲಿ ಕಡಿಮೆ ಅಪಾಯದ ಪರಿಸ್ಥಿತಿ ಇದೆ. "
                "ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ಗಮನಿಸುತ್ತಿರಿ."
        },

        "Malayalam": {
            "HIGH":
                f"{state} ൽ ഉയർന്ന അപകട മുന്നറിയിപ്പ്. ആവശ്യമായ "
                "സുരക്ഷാ നടപടികൾ സ്വീകരിക്കുകയും ഔദ്യോഗിക മുന്നറിയിപ്പുകൾ പാലിക്കുകയും ചെയ്യുക.",
            "MEDIUM":
                f"{state} ൽ മിതമായ അപകട മുന്നറിയിപ്പ്. ജാഗ്രത പാലിക്കുകയും "
                "ഔദ്യോഗിക കാലാവസ്ഥാ വിവരങ്ങൾ നിരീക്ഷിക്കുകയും ചെയ്യുക.",
            "LOW":
                f"{state} ൽ കുറഞ്ഞ അപകടസാധ്യതയാണ്. "
                "കാലാവസ്ഥാ വിവരങ്ങൾ നിരീക്ഷിക്കുക."
        },

        "Marathi": {
            "HIGH":
                f"{state} साठी उच्च जोखीम इशारा. कृपया आवश्यक "
                "सुरक्षा उपाय करा आणि अधिकृत आपत्ती सूचना पाळा.",
            "MEDIUM":
                f"{state} साठी मध्यम जोखीम इशारा. सावध राहा "
                "आणि अधिकृत हवामान माहिती तपासा.",
            "LOW":
                f"{state} मध्ये कमी जोखीमची परिस्थिती आहे. "
                "हवामान माहितीवर लक्ष ठेवा."
        },

        "Tamil": {
            "HIGH":
                f"{state} க்கு அதிக ஆபத்து எச்சரிக்கை. தேவையான "
                "பாதுகாப்பு நடவடிக்கைகளை எடுத்து அதிகாரப்பூர்வ எச்சரிக்கைகளைப் பின்பற்றவும்.",
            "MEDIUM":
                f"{state} க்கு நடுத்தர ஆபத்து எச்சரிக்கை. "
                "எச்சரிக்கையுடன் இருந்து வானிலை தகவல்களை கவனிக்கவும்.",
            "LOW":
                f"{state} இல் குறைந்த ஆபத்து நிலை உள்ளது. "
                "வானிலை தகவல்களை தொடர்ந்து கவனிக்கவும்."
        },

        "Urdu": {
            "HIGH":
                f"{state} کے لیے زیادہ خطرے کی وارننگ۔ براہ کرم ضروری "
                "حفاظتی اقدامات کریں اور سرکاری آفات کی وارننگ پر عمل کریں۔",
            "MEDIUM":
                f"{state} کے لیے درمیانے خطرے کی وارننگ۔ محتاط رہیں "
                "اور سرکاری موسمی معلومات پر نظر رکھیں۔",
            "LOW":
                f"{state} میں کم خطرے کی صورتحال ہے۔ "
                "موسمی معلومات پر نظر رکھیں۔"
        },

        "Punjabi": {
            "HIGH":
                f"{state} ਲਈ ਉੱਚ ਜੋਖਮ ਦੀ ਚੇਤਾਵਨੀ। ਕਿਰਪਾ ਕਰਕੇ ਲੋੜੀਂਦੇ "
                "ਸੁਰੱਖਿਆ ਉਪਾਅ ਕਰੋ ਅਤੇ ਸਰਕਾਰੀ ਚੇਤਾਵਨੀਆਂ ਦੀ ਪਾਲਣਾ ਕਰੋ।",
            "MEDIUM":
                f"{state} ਲਈ ਦਰਮਿਆਨੇ ਜੋਖਮ ਦੀ ਚੇਤਾਵਨੀ। ਸਾਵਧਾਨ ਰਹੋ "
                "ਅਤੇ ਸਰਕਾਰੀ ਮੌਸਮ ਜਾਣਕਾਰੀ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ।",
            "LOW":
                f"{state} ਵਿੱਚ ਘੱਟ ਜੋਖਮ ਦੀ ਸਥਿਤੀ ਹੈ। "
                "ਮੌਸਮ ਦੀ ਜਾਣਕਾਰੀ 'ਤੇ ਨਜ਼ਰ ਰੱਖੋ।"
        }
    }

    return warnings.get(
        language,
        warnings["English"]
    ).get(
        risk,
        warnings["English"]["LOW"]
    )


# =========================================================
# STATE AND LANGUAGE SELECTION
# =========================================================

col1, col2 = st.columns(2)

with col1:
    selected_state = st.selectbox(
        "📍 Select Northeast State",
        list(locations.keys())
    )

with col2:
    selected_language = st.selectbox(
        "🌐 Select Warning Language",
        list(languages.keys())
    )


lat, lon = locations[selected_state]


# =========================================================
# OPEN-METEO API
# =========================================================

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": lat,
    "longitude": lon,

    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "weather_code"
    ],

    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "precipitation_probability_max",
        "wind_speed_10m_max"
    ],

    "forecast_days": 7,
    "timezone": "auto"
}


# =========================================================
# FETCH WEATHER
# =========================================================

try:

    response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

    if response.status_code == 200:

        data = response.json()

        current = data["current"]
        daily = data["daily"]


        # =================================================
        # CURRENT WEATHER
        # =================================================

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        precipitation = current["precipitation"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        weather_text = weather_description(weather_code)


        # =================================================
        # RISK CALCULATION
        # =================================================

        risk, risk_score = calculate_risk(
            precipitation,
            wind_speed,
            humidity,
            temperature
        )


        # =================================================
        # CURRENT WEATHER SECTION
        # =================================================

        st.markdown("---")

        st.header(f"🌦️ Current Weather - {selected_state}")

        weather_col1, weather_col2 = st.columns(2)

        with weather_col1:

            st.metric(
                "🌡️ Temperature",
                f"{temperature:.1f} °C"
            )

            st.metric(
                "🌧️ Rainfall",
                f"{precipitation:.1f} mm"
            )

            st.metric(
                "💧 Humidity",
                f"{humidity:.0f}%"
            )

            st.metric(
                "💨 Wind Speed",
                f"{wind_speed:.1f} km/h"
            )


        with weather_col2:

            st.subheader("☁️ Weather Condition")

            st.success(weather_text)

            st.subheader("⚠️ Risk Assessment")

            if risk == "HIGH":
                st.error(
                    f"🔴 HIGH RISK\n\nRisk Score: {risk_score}"
                )

            elif risk == "MEDIUM":
                st.warning(
                    f"🟠 MEDIUM RISK\n\nRisk Score: {risk_score}"
                )

            else:
                st.success(
                    f"🟢 LOW RISK\n\nRisk Score: {risk_score}"
                )


        # =================================================
        # WARNING
        # =================================================

        st.markdown("---")

        st.header("🚨 Early Warning")

        warning = generate_warning(
            selected_state,
            risk,
            precipitation,
            wind_speed
        )

        if risk == "HIGH":
            st.error(warning)

        elif risk == "MEDIUM":
            st.warning(warning)

        else:
            st.success(warning)


        # =================================================
        # MULTILINGUAL WARNING
        # =================================================

        st.markdown("---")

        st.header("🔊 Multilingual Voice Warning")

        translated_warning = translate_warning(
            selected_state,
            risk,
            selected_language
        )

        st.info(translated_warning)

        if st.button("🔊 Generate & Play Warning"):

            try:

                language_code = languages[selected_language]

                audio_buffer = BytesIO()

                tts = gTTS(
                    text=translated_warning,
                    lang=language_code,
                    slow=False
                )

                tts.write_to_fp(audio_buffer)

                audio_buffer.seek(0)

                st.audio(
                    audio_buffer,
                    format="audio/mp3"
                )

            except Exception as e:

                st.error(
                    "Unable to generate voice warning. "
                    "Please check your internet connection."
                )


        # =================================================
        # 7-DAY FORECAST
        # =================================================

        st.markdown("---")

        st.header("📅 7-Day Weather Forecast")

        forecast_data = []

        for i in range(len(daily["time"])):

            forecast_data.append({
                "Date": daily["time"][i],
                "Max Temp (°C)": daily["temperature_2m_max"][i],
                "Min Temp (°C)": daily["temperature_2m_min"][i],
                "Rainfall (mm)": daily["precipitation_sum"][i],
                "Rain Probability (%)":
                    daily["precipitation_probability_max"][i],
                "Max Wind (km/h)":
                    daily["wind_speed_10m_max"][i]
            })

        forecast_df = pd.DataFrame(forecast_data)

        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # RISK MAP
        # =================================================

        st.markdown("---")

        st.header("🗺️ Northeast India Risk Map")

        northeast_map = folium.Map(
            location=[25.5, 93.5],
            zoom_start=6
        )


        # Add all 8 states

        for state, (state_lat, state_lon) in locations.items():

            try:

                state_params = {
                    "latitude": state_lat,
                    "longitude": state_lon,

                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "precipitation",
                        "wind_speed_10m",
                        "weather_code"
                    ],

                    "timezone": "auto"
                }

                state_response = requests.get(
                    weather_url,
                    params=state_params,
                    timeout=10
                )

                if state_response.status_code == 200:

                    state_data = state_response.json()

                    state_current = state_data["current"]

                    state_temperature = state_current[
                        "temperature_2m"
                    ]

                    state_humidity = state_current[
                        "relative_humidity_2m"
                    ]

                    state_rain = state_current[
                        "precipitation"
                    ]

                    state_wind = state_current[
                        "wind_speed_10m"
                    ]

                    state_risk, state_score = calculate_risk(
                        state_rain,
                        state_wind,
                        state_humidity,
                        state_temperature
                    )


                    # Risk marker color

                    if state_risk == "HIGH":
                        marker_color = "red"

                    elif state_risk == "MEDIUM":
                        marker_color = "orange"

                    else:
                        marker_color = "green"


                    popup_text = f"""
                    <b>{state}</b><br>
                    Risk: {state_risk}<br>
                    Temperature: {state_temperature:.1f} °C<br>
                    Rainfall: {state_rain:.1f} mm<br>
                    Humidity: {state_humidity:.0f}%<br>
                    Wind: {state_wind:.1f} km/h
                    """


                    folium.Marker(
                        location=[
                            state_lat,
                            state_lon
                        ],

                        popup=folium.Popup(
                            popup_text,
                            max_width=300
                        ),

                        tooltip=f"{state} - {state_risk}",

                        icon=folium.Icon(
                            color=marker_color,
                            icon="warning-sign"
                        )
                    ).add_to(northeast_map)


            except Exception:
                pass


        st_folium(
            northeast_map,
            width=None,
            height=550
        )


        # =================================================
        # MAP LEGEND
        # =================================================

        st.markdown(
            """
            ### 🟢 Risk Map Legend

            🔴 **HIGH** – Potentially hazardous conditions  
            
            🟠 **MEDIUM** – Conditions require caution  
            
            🟢 **LOW** – Normal/low-risk conditions
            """
        )


        # =================================================
        # ALERT INDICATORS
        # =================================================

        st.markdown("---")

        st.header("📢 Weather Alert Indicators")

        alert_col1, alert_col2 = st.columns(2)


        with alert_col1:

            if precipitation >= 20:

                st.error(
                    "🌧️ Heavy Rainfall Alert\n\n"
                    f"Current rainfall: {precipitation:.1f} mm"
                )

            elif precipitation >= 10:

                st.warning(
                    "🌦️ Rainfall Alert\n\n"
                    f"Current rainfall: {precipitation:.1f} mm"
                )

            else:

                st.success(
                    "☀️ No Significant Rainfall Alert"
                )


        with alert_col2:

            if wind_speed >= 40:

                st.error(
                    "💨 Strong Wind Alert\n\n"
                    f"Current wind speed: {wind_speed:.1f} km/h"
                )

            elif wind_speed >= 25:

                st.warning(
                    "💨 Moderate Wind Alert\n\n"
                    f"Current wind speed: {wind_speed:.1f} km/h"
                )

            else:

                st.success(
                    "🌿 No Significant Wind Alert"
                )


        # =================================================
        # LAST UPDATED
        # =================================================

        st.markdown("---")

        st.caption(
            f"🔄 Weather data automatically refreshes every 5 minutes."
        )

        st.caption(
            f"Last weather update: {current.get('time', 'N/A')}"
        )


        # =================================================
        # FOOTER
        # =================================================

        st.markdown("---")

        st.caption(
            "Weather: Open-Meteo API | "
            "Map: Folium/OpenStreetMap | "
            "Voice: Google Text-to-Speech (gTTS)"
        )

        st.caption(
            "⚠️ Disclaimer: Risk levels shown by this prototype "
            "are indicative and are not official government warnings. "
            "Always follow official disaster-management alerts."
        )


    else:

        st.error(
            f"Weather API error. Status code: {response.status_code}"
        )


except requests.exceptions.RequestException:

    st.error(
        "Unable to connect to the weather service. "
        "Please check your internet connection."
    )

except Exception as e:

    st.error(
        f"An unexpected error occurred: {str(e)}"
)
