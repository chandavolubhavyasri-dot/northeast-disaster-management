import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Northeast India Disaster Management",
    page_icon="🚨",
    layout="wide"
)
st_autorefresh(
    interval=10 * 60 * 1000,
    key="weather_refresh"
)
st.markdown("""
<style>
.stApp {
    background:
        linear-gradient(
            rgba(10, 35, 55, 0.82),
            rgba(5, 25, 45, 0.90)
        ),
        url("https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=2000&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.weather-card {
    background: rgba(255,255,255,0.15);
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    margin: 5px;
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚨 Northeast India Disaster Management")
st.subheader("🌦️ Weather Monitoring & Multilingual Early Warning System")

st.info(
    "Monitor weather conditions, assess disaster risk, "
    "view the Northeast India risk map and generate "
    "voice warnings in multiple Indian languages."
)


# =========================================================
# NORTHEAST INDIA STATES
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
# LANGUAGE OPTIONS
# =========================================================

language_options = {
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
# LANGUAGE SELECTION
# =========================================================

st.header("🗣️ Warning Language")

language = st.selectbox(
    "Select the language for the voice warning:",
    list(language_options.keys())
)

language_code = language_options[language]


# =========================================================
# STATE SELECTION
# =========================================================

st.header("📍 Location")

state = st.selectbox(
    "Select a Northeast Indian State:",
    list(locations.keys())
)

latitude, longitude = locations[state]


# =========================================================
# OPEN-METEO API
# =========================================================

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "weather_code"
    ],
    "hourly": [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "precipitation_probability",
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
# WEATHER DESCRIPTION
# =========================================================

def weather_description(code):

    if code == 0:
        return "☀️ Clear Sky"

    elif code in [1, 2, 3]:
        return "🌤️ Partly Cloudy"

    elif code in [45, 48]:
        return "🌫️ Fog"

    elif code in [51, 53, 55]:
        return "🌦️ Drizzle"

    elif code in [61, 63, 65]:
        return "🌧️ Rain"

    elif code in [66, 67]:
        return "🌧️ Freezing Rain"

    elif code in [71, 73, 75, 77]:
        return "❄️ Snow"

    elif code in [80, 81, 82]:
        return "🌧️ Rain Showers"

    elif code == 95:
        return "⛈️ Thunderstorm"

    elif code in [96, 99]:
        return "⛈️ Thunderstorm with Hail"

    return "🌦️ Unknown Weather"


# =========================================================
# RISK CALCULATION
# =========================================================

def calculate_risk(
    temperature,
    humidity,
    precipitation,
    wind_speed
):

    score = 0
    warnings = []

    # Rainfall
    if precipitation >= 50:
        score += 3
        warnings.append("Very heavy rainfall detected.")

    elif precipitation >= 20:
        score += 2
        warnings.append("Heavy rainfall detected.")

    elif precipitation >= 10:
        score += 1
        warnings.append("Moderate rainfall detected.")

    # Wind
    if wind_speed >= 60:
        score += 3
        warnings.append("Very strong wind detected.")

    elif wind_speed >= 40:
        score += 2
        warnings.append("Strong wind detected.")

    elif wind_speed >= 25:
        score += 1
        warnings.append("Moderate wind detected.")

    # Humidity
    if humidity >= 90:
        score += 1
        warnings.append("Very high humidity detected.")

    # Temperature
    if temperature >= 40:
        score += 2
        warnings.append("Extreme temperature detected.")

    # Risk level
    if score >= 6:
        risk = "HIGH"

    elif score >= 3:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return risk, warnings


# =========================================================
# RISK COLOR
# =========================================================

def risk_color(risk):

    if risk == "HIGH":
        return "red"

    elif risk == "MEDIUM":
        return "orange"

    return "green"


# =========================================================
# MULTILINGUAL WARNING TEXT
# =========================================================

def get_warning_text(risk, state, language):

    messages = {

        "English": {
            "HIGH":
                f"High risk alert for {state}. "
                "Please take necessary safety measures and "
                "follow official disaster warnings.",
            "MEDIUM":
                f"Medium risk alert for {state}. "
                "Please remain alert and monitor weather conditions.",
            "LOW":
                f"Low risk in {state}. "
                "Weather conditions are currently relatively stable."
        },

        "Hindi": {
            "HIGH":
                f"{state} में उच्च जोखिम की चेतावनी। "
                "कृपया आवश्यक सुरक्षा उपाय करें और आधिकारिक आपदा चेतावनियों का पालन करें।",
            "MEDIUM":
                f"{state} में मध्यम जोखिम की चेतावनी। "
                "कृपया सतर्क रहें और मौसम की स्थिति पर नजर रखें।",
            "LOW":
                f"{state} में कम जोखिम है। "
                "मौसम की स्थिति वर्तमान में अपेक्षाकृत स्थिर है।"
        },

        "Telugu": {
            "HIGH":
                f"{state} లో అధిక ప్రమాద హెచ్చరిక. "
                "దయచేసి అవసరమైన భద్రతా చర్యలు తీసుకోండి మరియు అధికారిక విపత్తు హెచ్చరికలను పాటించండి.",
            "MEDIUM":
                f"{state} లో మధ్యస్థ ప్రమాద హెచ్చరిక. "
                "దయచేసి అప్రమత్తంగా ఉండి వాతావరణ పరిస్థితులను గమనించండి.",
            "LOW":
                f"{state} లో తక్కువ ప్రమాదం ఉంది. "
                "ప్రస్తుతం వాతావరణ పరిస్థితులు సాధారణంగా స్థిరంగా ఉన్నాయి."
        },

        "Bengali": {
            "HIGH":
                f"{state}-এ উচ্চ ঝুঁকির সতর্কতা। "
                "দয়া করে প্রয়োজনীয় নিরাপত্তা ব্যবস্থা নিন এবং সরকারি দুর্যোগ সতর্কতা অনুসরণ করুন।",
            "MEDIUM":
                f"{state}-এ মাঝারি ঝুঁকির সতর্কতা। "
                "দয়া করে সতর্ক থাকুন এবং আবহাওয়ার পরিস্থিতি পর্যবেক্ষণ করুন।",
            "LOW":
                f"{state}-এ কম ঝুঁকি রয়েছে। "
                "বর্তমানে আবহাওয়ার পরিস্থিতি তুলনামূলকভাবে স্থিতিশীল।"
        },

        "Gujarati": {
            "HIGH":
                f"{state} માટે ઉચ્ચ જોખમની ચેતવણી. "
                "કૃપા કરીને જરૂરી સુરક્ષા પગલાં લો અને સત્તાવાર આપત્તિ ચેતવણીઓનું પાલન કરો.",
            "MEDIUM":
                f"{state} માટે મધ્યમ જોખમની ચેતવણી. "
                "કૃપા કરીને સાવચેત રહો અને હવામાનની સ્થિતિ પર નજર રાખો.",
            "LOW":
                f"{state} માં ઓછું જોખમ છે. "
                "હાલમાં હવામાનની સ્થિતિ પ્રમાણમાં સ્થિર છે."
        },

        "Kannada": {
            "HIGH":
                f"{state} ನಲ್ಲಿ ಹೆಚ್ಚಿನ ಅಪಾಯದ ಎಚ್ಚರಿಕೆ. "
                "ದಯವಿಟ್ಟು ಅಗತ್ಯ ಸುರಕ್ಷತಾ ಕ್ರಮಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ ಮತ್ತು ಅಧಿಕೃತ ವಿಪತ್ತು ಎಚ್ಚರಿಕೆಗಳನ್ನು ಅನುಸರಿಸಿ.",
            "MEDIUM":
                f"{state} ನಲ್ಲಿ ಮಧ್ಯಮ ಅಪಾಯದ ಎಚ್ಚರಿಕೆ. "
                "ದಯವಿಟ್ಟು ಎಚ್ಚರಿಕೆಯಿಂದಿರಿ ಮತ್ತು ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಯನ್ನು ಗಮನಿಸಿ.",
            "LOW":
                f"{state} ನಲ್ಲಿ ಕಡಿಮೆ ಅಪಾಯವಿದೆ. "
                "ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿ ಸಾಮಾನ್ಯವಾಗಿ ಸ್ಥಿರವಾಗಿದೆ."
        },

        "Malayalam": {
            "HIGH":
                f"{state} ൽ ഉയർന്ന അപകടസാധ്യതാ മുന്നറിയിപ്പ്. "
                "ദയവായി ആവശ്യമായ സുരക്ഷാ നടപടികൾ സ്വീകരിക്കുകയും ഔദ്യോഗിക ദുരന്ത മുന്നറിയിപ്പുകൾ പാലിക്കുകയും ചെയ്യുക.",
            "MEDIUM":
                f"{state} ൽ മിതമായ അപകടസാധ്യതാ മുന്നറിയിപ്പ്. "
                "ദയവായി ജാഗ്രത പാലിക്കുകയും കാലാവസ്ഥ നിരീക്ഷിക്കുകയും ചെയ്യുക.",
            "LOW":
                f"{state} ൽ കുറഞ്ഞ അപകടസാധ്യതയാണ്. "
                "നിലവിലെ കാലാവസ്ഥ താരതമ്യേന സ്ഥിരമാണ്."
        },

        "Marathi": {
            "HIGH":
                f"{state} साठी उच्च जोखमीचा इशारा. "
                "कृपया आवश्यक सुरक्षा उपाय करा आणि अधिकृत आपत्ती इशाऱ्यांचे पालन करा.",
            "MEDIUM":
                f"{state} साठी मध्यम जोखमीचा इशारा. "
                "कृपया सतर्क राहा आणि हवामान परिस्थितीवर लक्ष ठेवा.",
            "LOW":
                f"{state} मध्ये कमी धोका आहे. "
                "सध्या हवामानाची परिस्थिती तुलनेने स्थिर आहे."
        },

        "Tamil": {
            "HIGH":
                f"{state} பகுதியில் அதிக ஆபத்து எச்சரிக்கை. "
                "தயவுசெய்து தேவையான பாதுகாப்பு நடவடிக்கைகளை மேற்கொண்டு அதிகாரப்பூர்வ பேரிடர் எச்சரிக்கைகளைப் பின்பற்றவும்.",
            "MEDIUM":
                f"{state} பகுதியில் நடுத்தர ஆபத்து எச்சரிக்கை. "
                "தயவுசெய்து விழிப்புடன் இருந்து வானிலை நிலையை கண்காணிக்கவும்.",
            "LOW":
                f"{state} பகுதியில் குறைந்த ஆபத்து உள்ளது. "
                "தற்போது வானிலை நிலை ஒப்பீட்டளவில் நிலையாக உள்ளது."
        },

        "Urdu": {
            "HIGH":
                f"{state} کے لیے زیادہ خطرے کی وارننگ۔ "
                "براہ کرم ضروری حفاظتی اقدامات کریں اور سرکاری آفات کی وارننگ پر عمل کریں۔",
            "MEDIUM":
                f"{state} کے لیے درمیانے خطرے کی وارننگ۔ "
                "براہ کرم محتاط رہیں اور موسم کی صورتحال پر نظر رکھیں۔",
            "LOW":
                f"{state} میں کم خطرہ ہے۔ "
                "موجودہ موسمی صورتحال نسبتاً مستحکم ہے۔"
        },

        "Punjabi": {
            "HIGH":
                f"{state} ਲਈ ਉੱਚ ਖਤਰੇ ਦੀ ਚੇਤਾਵਨੀ। "
                "ਕਿਰਪਾ ਕਰਕੇ ਜ਼ਰੂਰੀ ਸੁਰੱਖਿਆ ਕਦਮ ਚੁੱਕੋ ਅਤੇ ਸਰਕਾਰੀ ਆਫ਼ਤ ਚੇਤਾਵਨੀਆਂ ਦੀ ਪਾਲਣਾ ਕਰੋ।",
            "MEDIUM":
                f"{state} ਲਈ ਦਰਮਿਆਨੇ ਖਤਰੇ ਦੀ ਚੇਤਾਵਨੀ। "
                "ਕਿਰਪਾ ਕਰਕੇ ਸਾਵਧਾਨ ਰਹੋ ਅਤੇ ਮੌਸਮ ਦੀ ਸਥਿਤੀ 'ਤੇ ਨਜ਼ਰ ਰੱਖੋ।",
            "LOW":
                f"{state} ਵਿੱਚ ਘੱਟ ਖਤਰਾ ਹੈ। "
                "ਮੌਜੂਦਾ ਮੌਸਮ ਦੀ ਸਥਿਤੀ ਮੁਕਾਬਲਤਨ ਸਥਿਰ ਹੈ।"
        }
    }

    return messages[language][risk]


# =========================================================
# GET WEATHER DATA
# =========================================================

try:

    response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

    if response.status_code == 200:

        data = response.json()
        # Get hourly weather data
hourly = data["hourly"]

hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(hourly["time"]),
    "Temperature (°C)": hourly["temperature_2m"],
    "Rain (mm)": hourly["precipitation"],
    "Rain Probability (%)": hourly["precipitation_probability"],
    "Humidity (%)": hourly["relative_humidity_2m"],
    "Wind (km/h)": hourly["wind_speed_10m"]
})

st.subheader("🕐 Hourly Weather Forecast")

st.dataframe(
    hourly_df.head(24),
    use_container_width=True,
    hide_index=True
)

        current = data["current"]
        daily = data["daily"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        precipitation = current["precipitation"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]


        # =================================================
        # CURRENT WEATHER
        # =================================================

        st.header(f"📍 Current Weather — {state}")

        st.write(
            weather_description(weather_code)
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🌡️ Temperature",
                f"{temperature} °C"
            )

        with col2:
            st.metric(
                "💧 Humidity",
                f"{humidity}%"
            )

        with col3:
            st.metric(
                "🌧️ Rainfall",
                f"{precipitation} mm"
            )

        with col4:
            st.metric(
                "💨 Wind Speed",
                f"{wind_speed} km/h"
            )


        # =================================================
        # RISK ASSESSMENT
        # =================================================

        risk, warnings = calculate_risk(
            temperature,
            humidity,
            precipitation,
            wind_speed
        )

        st.header("⚠️ Disaster Risk Assessment")

        if risk == "HIGH":
            st.error("🔴 HIGH RISK")

        elif risk == "MEDIUM":
            st.warning("🟠 MEDIUM RISK")

        else:
            st.success("🟢 LOW RISK")


        # =================================================
        # RISK INDICATORS
        # =================================================

        st.subheader("🚨 Weather Risk Indicators")

        if warnings:

            for warning in warnings:
                st.warning(warning)

        else:

            st.success(
                "No major weather risk indicators detected."
            )


        # =================================================
        # MULTILINGUAL VOICE WARNING
        # =================================================

        st.header("🔊 Multilingual AI Voice Warning")

        warning_text = get_warning_text(
            risk,
            state,
            language
        )

        st.write(
            f"**{language} warning:**"
        )

        st.info(warning_text)

        if st.button("🔊 Generate & Play Warning"):

            try:

                with st.spinner(
                    "Generating voice warning..."
                ):

                    tts = gTTS(
                        text=warning_text,
                        lang=language_code,
                        slow=False
                    )

                    audio_file = "warning.mp3"

                    tts.save(audio_file)

                with open(
                    audio_file,
                    "rb"
                ) as audio:

                    audio_bytes = audio.read()

                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )

            except Exception as e:

                st.error(
                    "Unable to generate voice warning. "
                    "Please check your internet connection "
                    f"or try another language. Error: {e}"
                )


        # =================================================
        # 7-DAY FORECAST
        # =================================================

        st.header("📅 7-Day Weather Forecast")

        forecast_data = {

            "Date":
                daily["time"],

            "Max Temperature (°C)":
                daily["temperature_2m_max"],

            "Min Temperature (°C)":
                daily["temperature_2m_min"],

            "Rainfall (mm)":
                daily["precipitation_sum"],

            "Rain Probability (%)":
                daily["precipitation_probability_max"],

            "Max Wind (km/h)":
                daily["wind_speed_10m_max"]
        }

        forecast_df = pd.DataFrame(
            forecast_data
        )

        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # INTERACTIVE NORTHEAST INDIA MAP
        # =================================================

        st.header(
            "🗺️ Northeast India Interactive Risk Map"
        )

        st.write(
            "Tap a state marker to view its current "
            "weather conditions and risk level."
        )

        northeast_map = folium.Map(
            location=[
                25.5,
                92.5
            ],
            zoom_start=6,
            tiles="OpenStreetMap"
        )


        # =================================================
        # MAP STATE MARKERS
        # =================================================

        for state_name, coords in locations.items():

            try:

                state_params = {

                    "latitude": coords[0],

                    "longitude": coords[1],

                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "precipitation",
                        "wind_speed_10m"
                    ],

                    "timezone": "auto"
                }

                state_response = requests.get(
                    weather_url,
                    params=state_params,
                    timeout=10
                )

                if state_response.status_code == 200:

                    state_data = (
                        state_response.json()
                    )

                    state_current = (
                        state_data["current"]
                    )

                    state_temp = (
                        state_current[
                            "temperature_2m"
                        ]
                    )

                    state_humidity = (
                        state_current[
                            "relative_humidity_2m"
                        ]
                    )

                    state_rain = (
                        state_current[
                            "precipitation"
                        ]
                    )

                    state_wind = (
                        state_current[
                            "wind_speed_10m"
                        ]
                    )

                    state_risk, state_warnings = (
                        calculate_risk(
                            state_temp,
                            state_humidity,
                            state_rain,
                            state_wind
                        )
                    )

                    color = risk_color(
                        state_risk
                    )

                    popup_text = f"""
                    <div style="font-size:14px">
                    <b>{state_name}</b><br><br>
                    Risk Level:
                    <b>{state_risk}</b><br>
                    Temperature: {state_temp} °C<br>
                    Humidity: {state_humidity}%<br>
                    Rainfall: {state_rain} mm<br>
                    Wind Speed: {state_wind} km/h
                    </div>
                    """

                    folium.Marker(

                        location=coords,

                        popup=folium.Popup(
                            popup_text,
                            max_width=300
                        ),

                        tooltip=(
                            f"{state_name} - "
                            f"{state_risk} RISK"
                        ),

                        icon=folium.Icon(
                            color=color,
                            icon="info-sign"
                        )

                    ).add_to(
                        northeast_map
                    )

            except Exception:
                continue


        # =================================================
        # DISPLAY MAP
        # =================================================

        map_data = st_folium(
            northeast_map,
            width=1100,
            height=600
        )


        # =================================================
        # MAP LEGEND
        # =================================================

        st.subheader("📊 Risk Map Legend")

        legend1, legend2, legend3 = st.columns(3)

        with legend1:
            st.error("🔴 HIGH RISK")

        with legend2:
            st.warning("🟠 MEDIUM RISK")

        with legend3:
            st.success("🟢 LOW RISK")


        # =================================================
        # RAINFALL ALERT
        # =================================================

        st.header("🌧️ Rainfall Monitoring")

        maximum_rain = max(
            daily["precipitation_sum"]
        )

        if maximum_rain >= 50:

            st.error(
                f"🚨 Very Heavy Rainfall Alert — "
                f"{maximum_rain} mm forecast."
            )

        elif maximum_rain >= 20:

            st.warning(
                f"⚠️ Heavy Rainfall Alert — "
                f"{maximum_rain} mm forecast."
            )

        else:

            st.success(
                "✅ No heavy rainfall threshold detected "
                "in the forecast."
            )


        # =================================================
        # WIND ALERT
        # =================================================

        st.header("💨 Wind Monitoring")

        maximum_wind = max(
            daily["wind_speed_10m_max"]
        )

        if maximum_wind >= 60:

            st.error(
                f"🚨 Strong Wind Alert — "
                f"{maximum_wind} km/h forecast."
            )

        elif maximum_wind >= 40:

            st.warning(
                f"⚠️ Moderate Wind Alert — "
                f"{maximum_wind} km/h forecast."
            )

        else:

            st.success(
                "✅ Wind conditions are below "
                "the alert threshold."
            )


        # =================================================
        # FOOTER
        # =================================================

        st.divider()

        st.caption(
            "🌦️ Weather: Open-Meteo API | "
            "🗺️ Map: Folium/OpenStreetMap | "
            "🔊 Voice: Google Text-to-Speech (gTTS)"
        )

        st.caption(
            "⚠️ Risk levels are application-generated "
            "prototype indicators. They are not official "
            "government disaster warnings."
        )


    else:

        st.error(
            "❌ Unable to retrieve weather data. "
            f"API status code: {response.status_code}"
        )


except requests.exceptions.Timeout:

    st.error(
        "⏱️ Weather service timed out. "
        "Please try again."
    )


except requests.exceptions.RequestException as e:

    st.error(
        f"🌐 Network error: {e}"
    )


except Exception as e:

    st.error(
        f"❌ Unexpected error: {e}"
            )
