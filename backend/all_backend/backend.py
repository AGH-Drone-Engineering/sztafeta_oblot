from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import requests
import json
import socket
import uvicorn
from createmission import MissionPlanner


app = FastAPI()

# Model danych do wysyłania współrzędnych (ESP32)
class Coordinates(BaseModel):
    long: float
    lat: float
    altitude: float
    delay: float
    servo_value: int
    ip: str

# Model danych do przetwarzania pliku JSON
class DataFramePayload(BaseModel):
    data: str
    ip: str
    port: int
    height: int


# Funkcja sprawdzająca połączenie z urządzeniem (ESP32)
def check_connection(ip: str, port: int = 80, timeout: int = 5) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False


# Endpoint do wysyłania współrzędnych (ESP32)
@app.post("/streamlit-coordinates")
def send_coordinates(coordinates: Coordinates):
    url = f"http://{coordinates.ip}/set-coordinates"
    
    # Sprawdzenie połączenia z urządzeniem
    if not check_connection(coordinates.ip):
        print(f"Cannot connect to device at {coordinates.ip}")
        raise HTTPException(status_code=400, detail=f"Cannot connect to device at {coordinates.ip}")
    
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "long": coordinates.long,
        "lat": coordinates.lat,
        "altitude": coordinates.altitude,
        "delay": coordinates.delay,
        "servo_value": coordinates.servo_value
    }
    print(data)
    try:
        # Wysłanie danych w formacie JSON do wskazanego URL
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return {"message": "Data sent successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


# Funkcja do parsowania pojedynczego wiersza z danych DataFrame
def parse_row(row):
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        if row['drop'] == 0:
            return {"add_waypoint": [row['latitude'], row['longitude']], "delay": row['delay']}
        elif row['drop'] == 1 and pd.notna(row['servo']):
            if pd.notna(row['drop_delay']):
                return {"add_waypoint": [row['latitude'], row['longitude']], "delay": row['delay'], 
                        "set_servo": row['servo'], "drop_delay": row['drop_delay']}
    elif pd.isna(row['latitude']) and pd.isna(row['longitude']) and pd.notna(row['delay']):
        return {"delay": row['delay']}
    return None

# Funkcja do parsowania całego DataFrame
def parse_dataframe(df):
    results = []
    for _, row in df.iterrows():
        result = parse_row(row)
        if result:
            results.append(result)
    return results

# Endpoint do przetwarzania pliku JSON i obsługi misji
@app.post("/upload")
async def upload(payload: DataFramePayload):
    data = payload.data
    if data:
        pd.options.display.float_format = '{:.8f}'.format
        df = pd.read_json(data, orient='split')
        
        ip, port = payload.ip, payload.port
        height = payload.height
        parsed_data = parse_dataframe(df)
        try:
            planner = MissionPlanner(f'udpin:{ip}:{port}')
        except Exception as e:
            return {"message": "Cannot communicate with vehicle: " + str(e)}, 400
        
        try:
            # Dodanie punktu startowego (takeoff)
            planner.add_takeoff(altitude=height)
            
            # Przetwarzanie komend z parsowanego DataFrame
            for command in parsed_data:
                if ('add_waypoint' in command and 'delay' in command and 
                    'set_servo' in command and 'drop_delay' in command):
                    planner.add_waypoint(lat=command['add_waypoint'][0], lon=command['add_waypoint'][1], 
                                         altitude=height, delay=command['delay'])
                    planner.set_servo(servo_number=command['set_servo'], pwm=1500)
                    planner.set_delay(delay_seconds=command['drop_delay'])
                elif 'add_waypoint' in command and 'delay' in command:
                    planner.add_waypoint(lat=command['add_waypoint'][0], lon=command['add_waypoint'][1], 
                                         altitude=height, delay=command['delay'])
                elif 'delay' in command:
                    planner.set_delay(delay_seconds=command['delay'])
                else:
                    return {"message": f"Invalid data received: {command}"}, 400
            
            # Powrót do punktu startowego (RTL)
            planner.add_return_to_launch()
            
            mission_upload_status = planner.upload_mission()
            planner.close_connection()
            if mission_upload_status == True:
                return {"message": "Data received successfully"}
            else:
                return {"message": "Mission upload failed"}, 400
            
        except Exception as e:
            return {"message": str(e)}, 400

    else:
        return {"message": "No data received"}, 400


# Uruchomienie aplikacji
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
