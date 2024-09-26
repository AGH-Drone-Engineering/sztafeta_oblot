import streamlit as st
import requests

st.title("ESP Control Panel")

# API endpoint
api_url = "http://localhost:8001"

# Pobranie dostępnych urządzeń ESP
response = requests.get(f"{api_url}/devices")
devices = response.json()

# Wybranie urządzenia
selected_device = st.selectbox("Select ESP device", list(devices.keys()))

# Podanie wartości zmiennych
lat = st.number_input("Enter latitute", value=0)
long = st.number_input("Enter longtitute", value=0)

if st.button("Send Data"):
    # Wysyłanie danych do wybranego urządzenia
    response = requests.post(f"{api_url}/send-data/{selected_device}", params={"lat": lat, "long": long})
    if response.status_code == 200:
        st.success("Data sent successfully")
    else:
        st.error(f"Error: {response.text}")
