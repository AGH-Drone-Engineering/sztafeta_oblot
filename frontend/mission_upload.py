import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from datetime import datetime

# Funkcja do dodawania punktu GPS do danych
def add_gps_point(data, lat, lon, timestamp):
    new_point = pd.DataFrame({'latitude': [lat], 'longitude': [lon], 'timestamp': [timestamp]})
    data = pd.concat([data, new_point], ignore_index=True)
    return data

# Funkcja do usuwania punktu GPS z danych
def remove_gps_point(data, index):
    data = data.drop(index).reset_index(drop=True)
    return data

# Funkcja do wyświetlenia mapy z punktami GPS połączonymi liniami
def show_map(data):
    if not data.empty:
        # Tworzenie mapy z domyślną lokalizacją (pierwszy punkt)
        center_lat = data['latitude'].mean()
        center_lon = data['longitude'].mean()
        map_ = folium.Map(location=[center_lat, center_lon], zoom_start=12, )
        
        # Dodawanie punktów GPS do mapy
        for _, row in data.iterrows():
            folium.Marker(location=[row['latitude'], row['longitude']], 
                          popup=f"Time: {row['timestamp']}").add_to(map_)
        
        # Połączenie punktów liniami
        folium.PolyLine(locations=data[['latitude', 'longitude']].values.tolist(), color='blue').add_to(map_)
        
        # Dopasowanie mapy do wszystkich punktów
        sw = data[['latitude', 'longitude']].min().values.tolist()
        ne = data[['latitude', 'longitude']].max().values.tolist()
        map_.fit_bounds([sw, ne])
        
        # Wyświetlenie mapy w Streamlit
        folium_static(map_)
    else:
        st.warning("No GPS data available to display.")

# Nagłówek strony
st.title("GPS Data Viewer")

# Tworzenie pustego DataFrame na dane GPS
if 'gps_data' not in st.session_state:
    st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp'])

# Inicjalizacja wartości domyślnych pól
if 'lat' not in st.session_state:
    st.session_state.lat = 0.0

if 'lon' not in st.session_state:
    st.session_state.lon = 0.0

# Formularz do wprowadzania danych GPS
st.subheader("Enter GPS Coordinates ui")

lat = st.number_input("Latitude", format="%.6f", value=st.session_state.lat, key="lat_input")
lon = st.number_input("Longitude", format="%.6f", value=st.session_state.lon, key="lon_input")

# Pobranie aktualnego czasu jako timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.button("Add Point"):
    if len(st.session_state.gps_data) < 15:
        st.session_state.gps_data = add_gps_point(st.session_state.gps_data, lat, lon, timestamp)
        st.success(f"Point added: ({lat}, {lon}) at {timestamp}")
        
        # Resetowanie pól
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
    else:
        st.warning("You can add up to 15 points only.")

# Wyświetlenie tabeli z danymi
st.subheader("Data Preview")
st.write(st.session_state.gps_data)

# Opcje usuwania punktów
if not st.session_state.gps_data.empty:
    st.subheader("Manage Points")

    # Wybór punktu do usunięcia
    point_to_remove = st.selectbox("Select a point to remove", st.session_state.gps_data.index)

    if st.button("Remove Selected Point"):
        st.session_state.gps_data = remove_gps_point(st.session_state.gps_data, point_to_remove)
        st.success(f"Point {point_to_remove} removed.")
    
    # Usunięcie wszystkich punktów
    if st.button("Remove All Points"):
        st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp'])
        st.success("All points removed.")

# Przycisk "Upload Mission"
if st.button("Upload Mission"):
    if not st.session_state.gps_data.empty:
        print("Uploaded Mission Points:")
        print(st.session_state.gps_data)
        st.success("Mission uploaded successfully.")
    else:
        st.warning("No points to upload.")

# Wyświetlenie mapy
st.subheader("Map")
show_map(st.session_state.gps_data)
