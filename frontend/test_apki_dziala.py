import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from datetime import datetime
import requests
import numpy as np

class GPSDataViewer:
    def __init__(self):
        if 'gps_data' not in st.session_state:
            st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp', 'delay', 'drop', 'servo', 'drop_delay'])
        if 'lat' not in st.session_state:
            st.session_state.lat = 53.0190701
        if 'lon' not in st.session_state:
            st.session_state.lon = 20.8802902
        if 'last_clicked_location' not in st.session_state:
            st.session_state.last_clicked_location = None
        st.session_state.edit_index = None

    def add_gps_point(self, lat, lon, delay, drop, servo, drop_delay, index=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pd.options.display.float_format = '{:.8f}'.format
        new_point = pd.DataFrame({
            'latitude': [lat], 
            'longitude': [lon], 
            'timestamp': [timestamp],
            'delay': [delay],
            'drop': [drop],
            'servo': [servo],
            'drop_delay': [drop_delay]
        })

        if index is not None:
            st.session_state.gps_data.iloc[index] = new_point.iloc[0]
        else:
            st.session_state.gps_data = pd.concat([st.session_state.gps_data, new_point], ignore_index=True)

        return st.session_state.gps_data

    def remove_gps_point(self, index):
        st.session_state.gps_data = st.session_state.gps_data.drop(index).reset_index(drop=True)
        return st.session_state.gps_data

    def on_map_click(self, location):
        st.session_state.last_clicked_location = location

    def show_map(self):
        data = st.session_state.gps_data.dropna(subset=['latitude', 'longitude'])  # Usunięcie punktów z NaN
        if not data.empty:
            center_lat = data['latitude'].mean()
            center_lon = data['longitude'].mean()
        else:
            center_lat = st.session_state.lat
            center_lon = st.session_state.lon
        
        map_ = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        if not data.empty:
            for _, row in data.iterrows():
                popup_text = f"Lat: {row['latitude']}<br>Lon: {row['longitude']}"
                if row['delay']:
                    popup_text += f"<br>Delay after match: {row['delay']}s"
                if row['drop']:
                    popup_text += f"<br>Servo {row['servo']}, Delay after servo: {row['drop_delay']}s"
                folium.Marker(location=[row['latitude'], row['longitude']], 
                              popup=popup_text).add_to(map_)
            
            folium.PolyLine(locations=data[['latitude', 'longitude']].values.tolist(), color='blue').add_to(map_)
        
        map_.add_child(folium.LatLngPopup())

        folium_static(map_)

    def main(self):
        st.title("GPS Data Viewer")
        
        st.subheader("Choose Action")
        action = st.radio("Select an action", ('Add Waypoint', 'Add Delay'))

        if action == 'Add Waypoint':
            st.subheader("Enter WAYPOINT Coordinates")
            lat = st.number_input("Latitude", format="%.8f", value=st.session_state.lat, key="lat_input", step=0.0000001)
            lon = st.number_input("Longitude", format="%.8f", value=st.session_state.lon, key="lon_input", step=0.0000001)
            
            delay = st.number_input("Delay at this point (seconds)", min_value=0, step=1)
            drop = st.checkbox("Payload drop at this point?")
            servo = st.selectbox("Select Servo for drop", options=[1, 2, 3, 4]) if drop else None
            drop_delay = st.number_input("Delay before drop (seconds)", min_value=0, step=1) if drop else None
            
            if st.button("Add Point"):
                if st.session_state.edit_index is not None:
                    self.add_gps_point(lat, lon, delay, drop, servo, drop_delay, index=st.session_state.edit_index)
                    st.success(f"Point {st.session_state.edit_index} updated.")
                    st.session_state.edit_index = None
                else:
                    if len(st.session_state.gps_data) < 30:
                        self.add_gps_point(lat, lon, delay, drop, servo, drop_delay)
                        st.success(f"Point added: ({lat}, {lon}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        st.session_state.lat = 53.0190700
                        st.session_state.lon = 20.8802900
                    else:
                        st.warning("You can add up to 15 points only.")
        
        elif action == 'Add Delay':
            delay = st.number_input("Enter Delay (seconds)", min_value=1, step=1)
            if st.button("Add Delay"):
                if len(st.session_state.gps_data) < 30:
                    self.add_gps_point(np.nan, np.nan, delay, np.nan, np.nan, np.nan)
                    st.success(f"Delay added: {delay} seconds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.warning("You can add up to 15 points only.")

        st.subheader("Data Preview")
        st.write(st.session_state.gps_data)
        
        if not st.session_state.gps_data.empty:
            st.subheader("Manage Points")
            point_to_remove = st.selectbox("Select a point to remove", st.session_state.gps_data.index)
            if st.button("Remove Selected Point"):
                self.remove_gps_point(point_to_remove)
                st.success(f"Point {point_to_remove} removed.")
                st.rerun()
            
            if st.button("Remove All Points"):
                st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp', 'delay', 'drop', 'servo', 'drop_delay'])
                st.success("All points removed.")
                st.rerun()
        
        if st.session_state.last_clicked_location is not None:
            st.subheader("Add Waypoint from Map Click")
            clicked_lat, clicked_lon = st.session_state.last_clicked_location
            st.write(f"Clicked location: Latitude: {clicked_lat}, Longitude: {clicked_lon}")
            
            if st.button("Add Clicked Point"):
                if len(st.session_state.gps_data) < 15:
                    self.add_gps_point(clicked_lat, clicked_lon, delay, drop, servo, drop_delay)
                    st.success(f"Point added: ({clicked_lat}, {clicked_lon}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.session_state.last_clicked_location = None
                else:
                    st.warning("You can add up to 15 points only.")
        st.subheader("Map")
        self.show_map()
        
        st.subheader("Server Connection Settings")
        ip_address = st.text_input("Enter server IP address", value="127.0.0.1")
        port = st.text_input("Enter server port", value="14550")
        height = st.number_input("Height Operation", key="height", step=1, value=10)
            
        if st.button("Upload Mission"):
            if not st.session_state.gps_data.empty:
                url = "http://localhost:8001/upload"  # Adres serwera FastAPI
                # Konwersja do JSON z zaokrągleniem do 8 miejsc po przecinku
                data_json = st.session_state.gps_data.round(8).to_json(orient='split')
                try:
                    response = requests.post(url, json={"data": data_json, "ip": ip_address, 
                                                        "port": port, "height": height})
                    if response.status_code == 200:
                        st.success("Mission uploaded successfully.")
                    else:
                        st.error(f"Failed to upload data. Server responded with status code {response.status_code}.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to upload data. Error: {str(e)}")
            else:
                st.warning("No points to upload.")

# To use the class:
viewer = GPSDataViewer()
viewer.main()