from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import socket
import uvicorn  # Dodane

app = FastAPI()

# Model danych
class Coordinates(BaseModel):
    long: float
    lat: float
    altitude: float
    delay: float
    servo_value: int
    ip: str  # Dodano pole IP urządzenia

# Funkcja sprawdzająca połączenie z urządzeniem
def check_connection(ip: str, port: int = 80, timeout: int = 5) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False

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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)